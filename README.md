# STONKZILLA CLI

STONKZILLA CLI is a Python cli tool that allows to plot stock price data and a set of supported indicators.  
Data for calculations and plotting is sourced from yfinance API by default or AlphaVantage (free, requires API key) if configured.     
The stock price data can be plot using lines or candlesticks. Indicators that generally have values close to prices are being plot on the price subplot, oscillators/momentum indicators get separate subplots for good readability.   
Supported indicators:    
1. Simple moving average (SMA),   
2. Exponential moving average (EMA),    
3. Bollinger Bands (BBANDS),
4. Fibonacci Retracements (FIBO),   
5. On-Balance Volume (OBV),

Oscilating indicators:
1. Relative Strength Index (RSI),
2. Average Directional Index (ADX),
3. Moving Average Convergence Divergence (MACD)

When entering indicators either in config.yaml or in terminal, use the same format:   
**INDICATOR_NAME:PARAMS**    
if indicator takes more than one parameters the next parameters are supposed to
be enetered spaced with dashes:      
**INDICATOR_NAME:PARAMS-PARAMS2-...**

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install stonkzilla
```
Or clone the repo and install dependecies:
```bash
git clone https://github.com/PraygeG/Market-Indicator-Cli.git
cd directory
pip install -r requirements.txt
```

## Usage
The most basic usage of the tool and the most limiting is to simply run it without any arguments.  
You'll be prompted to enter comma-separated list of tickers, start date, end date, interval and at least one indicator with parameters, this way of use deliver absolute minimum abilities of the tool.  

If you decided to clone the repo:
```bash
python -m stonkzilla.main [args]
```
or if you decided to pip install:
```bash
stonkzilla [args]
```
**To get help with arguments and get access to examples use help argument:**
```bash
python -m stonkzilla.main --help  OR  stonkzilla --help
```
## Reccommended usage
The tool supports running from YAML config file, which is highly recommended to avoid typing in the same arguments over and over after you'll find your favourite set of settings, this way is also better for plotting larger amount of charts.   
The tool supports automatic plot saving to specified directory, in specified format, in specified DPI if raster format was chosen. Example config file with helping will always be in the package directory no matter which way you decide to install. If the path isn't recognized when config mode is on, the program will fall back to the default config file inside a package directory:
```bash
stonkzilla -c <config_path> or python -m stonkzilla.main -c <config_path>
```

## License

[MIT](https://choosealicense.com/licenses/mit/)