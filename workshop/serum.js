use anchor_lang::prelude::*;
use anchor_spl::dex;
use anchor_spl::dex::serum_dex::instruction::SelfTradeBehavior;
use anchor_spl::dex::serum_dex::matching::{OrderType, Side as SerumSide};
use anchor_spl::dex::serum_dex::state::MarketState;
use anchor_spl::token;
use solana_program::declare_id;
use std::num::NonZeroU64;

declare_id!("22Y43yTVxuUkoRKdm9thyRhQ3SdgQS7c7kB6UNCiaczD");  

mod empty {
    use super::*;
    declare_id!("HJt8Tjdsc9ms9i4WCZEzhzr4oyf3ANcdzXrNdLPFqm3M");
}




pub fn init_account<'info>(ctx: Context<'_, '_, '_, 'info, InitAccount<'info>>) -> Result<()> {
        let ctx = CpiContext::new(ctx.accounts.dex_program.clone(), ctx.accounts.into());
        dex::init_open_orders(ctx)?;
        Ok(())
    }


pub fn swap<'info>(
        ctx: Context<'_, '_, '_, 'info, Swap<'info>>,
        side: Side,
        amount: u64,
        min_exchange_rate: ExchangeRate,
    )    -> Result<()> {
        let mut min_exchange_rate = min_exchange_rate;

        // Side determines swap direction.
        let (from_token, to_token) = match side {
            Side::Bid => (&ctx.accounts.pc_wallet, &ctx.accounts.market.coin_wallet),
            Side::Ask => (&ctx.accounts.market.coin_wallet, &ctx.accounts.pc_wallet),
        };

        // Token balances before the trade.
        let from_amount_before = token::accessor::amount(from_token)?;
        let to_amount_before = token::accessor::amount(to_token)?;

        // Execute trade.
        let orderbook: OrderbookClient<'info> = (&*ctx.accounts).into();
        match side {
            Side::Bid => orderbook.buy(amount, None)?,
            Side::Ask => orderbook.sell(amount, None)?,
        };
        orderbook.settle(referral)?;

        // Token balances after the trade.
        let from_amount_after = token::accessor::amount(from_token)?;
        let to_amount_after = token::accessor::amount(to_token)?;

        //  Calculate the delta, i.e. the amount swapped.
        let from_amount = from_amount_before.checked_sub(from_amount_after).unwrap();
        let to_amount = to_amount_after.checked_sub(to_amount_before).unwrap();

        // Safety checks.
        apply_risk_checks(DidSwap {
            authority: *ctx.accounts.authority.key,
            given_amount: amount,
            min_exchange_rate,
            from_amount,
            to_amount,
            quote_amount: 0,
            spill_amount: 0,
            from_mint: token::accessor::mint(from_token)?,
            to_mint: token::accessor::mint(to_token)?,
            quote_mint: match side {
                Side::Bid => token::accessor::mint(from_token)?,
                Side::Ask => token::accessor::mint(to_token)?,
            },
        })?;

        Ok(())
    }



#[error]
pub enum ErrorCode {
    #[msg("The tokens being swapped must have different mints")]
    SwapTokensCannotMatch,
    #[msg("Slippage tolerance exceeded")]
    SlippageExceeded,
    #[msg("No tokens received when swapping")]
    ZeroSwap,
}