# Objective

This python project tests multiple trading strategies on historical data. Any winning strategies are implemented into a bot.

## How we do it

We use the RBI system to implement our trading strategies

### 1. Research (R)

Research trading strategies on the internet using various resources such as google scholar, youtube, twitter, reddit, etc.

### 2. Backtest (B)

Test the strategy using historical data by using the backtrader library.

### 3. Implement (I)

Any winning strategies are implemented into a bot to trade on crypto exchanges or DeFi exchanges.

## Strategy / Bot Naming Scheme

Strategy names are defined differently based on if it is a Backtest strategy or a bot

If it is a backtest strategy we use the following naming scheme: `<index>_bt_strategy`, where index is a number.
If it is a bot we use the following naming scheme: `<index>_bot`, where index is a number.

The `index` number is a incremented number that is used to keep track of the strategy / bot.

If a bot has the same index as a backtest strategy, then the bot must implement the same strategy as the one defined in the backtest strategy.

i.e.

- If 001_bt_strategy tests a SMA strategy, 001_bot must implement that SMA strategy.
- If 002_bt_strategy tests a Bollinger Bands strategy, 002_bot must implement that Bollinger Bands strategy.
- If 003_bt_strategy tests a RSI strategy, 003_bot must implement that RSI strategy.
- etc.

## Commenting

At the top of every python file, there should be a comment that describes the strategy being used and the reason why its being used in the way it is.

## Disclaimer

The project is a work in progress and is not ready for production use.
