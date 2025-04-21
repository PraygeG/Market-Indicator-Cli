from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

class Plotterly:

    def __init__(self, title: str = 'Stock data with indicators'):
        self.title = title

    def plot(self, data: pd.DataFrame, indicators: dict, column: str = 'Close', company_name: str = "Unknown"):
        is_multiindex = isinstance(data.columns, pd.MultiIndex)

        def get_data_column(df: pd.DataFrame, col_name, ticker=None):
            if is_multiindex:
                if ticker:
                    return df[(col_name, ticker)]
                else:
                    available_tickers = df.columns.get_level_values(1).unique()
                    if len(available_tickers) > 0:
                        return df[(col_name, available_tickers[0])]
            else:
                return df[col_name]
            return None
        def get_indicator_data(indicator_series_or_df):
            if isinstance(indicator_series_or_df, pd.DataFrame):
                if 'MACD' in indicator_series_or_df.columns:
                    return indicator_series_or_df
                
                if isinstance(indicator_series_or_df.columns, pd.MultiIndex):
                    return indicator_series_or_df.iloc[:, 0]
                elif len(indicator_series_or_df) == 1:
                    return indicator_series_or_df.iloc[:, 0]
                else:
                    return indicator_series_or_df
            else:
                return indicator_series_or_df
        data = data.sort_index()

        print(f"Data shape: {data.shape}")
        print(f"Data index type: {type(data.index)}")
        print(f"Data columns: {data.columns}")
        print(f"Price column range: {data[column].min()} to {data[column].max()}")

        has_macd = any("MACD" in name for name in indicators)
        has_bbands = any("BBANDS" in name for name in indicators)
        has_rsi = any("RSI" in name for name in indicators)
        has_obv = any("OBV" in name for name in indicators)
        subplot_count = 1 + has_macd + has_bbands + has_rsi + has_obv

        fig = make_subplots(
            rows=subplot_count,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights= [3] + [1] * (subplot_count - 1)
        )
        price_data = get_data_column(data, column)

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=price_data,
                name=column,
                mode='lines',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        current_row = 1

        for name, (series, params) in indicators.items():
            if name in ["EMA", "SMA"]:
                param_text = "_".join(map(str, params)) if params else ""
                display_name = f"{name}_{param_text}" if param_text else name

                indicator_data = get_indicator_data(series)

                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicator_data,
                        name=display_name,
                        mode='lines',
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )

        if has_macd:
            current_row += 1
            macd_key = next(name for name in indicators if "MACD" in name)
            macd_data = indicators[macd_key][0]

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=macd_data["MACD"],
                    name="MACD lines",
                    mode='lines',
                    line=dict(color='orange')
                ),
                row=current_row, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=macd_data["Signal"],
                    name="Signal line",
                    mode='lines',
                    line=dict(color='green')
                ),
                row=current_row, col=1
            )
            histogram = macd_data["MACD"] - macd_data["Signal"]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=histogram,
                    name="MACD Histogram",
                    marker_color=['green' if val >= 0 else 'red' for val in histogram]
                ),
                row=current_row, col=1
            )
        if has_bbands:
            current_row += 1
            bbands_key = next(name for name in indicators if "BBANDS" in name)
            bbands_data = indicators[bbands_key][0]
            for band, color in [("upper_band", "red"), ("middle_band", "blue"), ("lower_band", "green")]:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=bbands_data[band],
                        name=band.replace("_", " ").title(),
                        mode='lines',
                        line=dict(color=color)
                    ),
                    row=current_row, col=1
                )
        if has_rsi:
            current_row += 1
            rsi_key = next(name for name in indicators if "RSI" in name)
            rsi_series = indicators[rsi_key][0]

            rsi_data = get_indicator_data(rsi_series)

            print(f"RSI min: {rsi_data.min()}, max: {rsi_data.max()}, NaN count: {rsi_data.isna().sum()}")
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=rsi_data,
                    name="RSI",
                    mode='lines',
                    line=dict(color='purple')
                ),
                row=current_row, col=1
            )
            fig.add_hline(y=70, line=dict(color='red', dash='dash'), row=current_row, col=1)
            fig.add_hline(y=30, line=dict(color='green', dash='dash'), row=current_row, col=1)

        if has_obv:
            current_row += 1
            obv_key = next(name for name in indicators if "OBV" in name)
            obv_series = indicators[obv_key][0]

            obv_data = get_indicator_data(obv_series)

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=obv_data,
                    name="OBV",
                    mode='lines',
                    line=dict(color='green')
                ),
                row=current_row, col=1
            )
        fig.update_layout(
            height=300 + 200 * subplot_count,
            title_text=f"{self.title} - {company_name}",
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        fig.update_yaxes(title_text="Price", row=1, col=1)
        current_row = 2

        if has_macd:
            fig.update_yaxes(title_text="MACD", row=current_row, col=1)
            current_row += 1
        if has_bbands:
            fig.update_yaxes(title_text="Bollinger Bands", row=current_row, col=1)
            current_row += 1
        if has_rsi:
            fig.update_yaxes(title_text="RSI", row=current_row, col=1)
            current_row += 1
        if has_obv:
            fig.update_yaxes(title_text="OBV", row=current_row, col=1)

        fig.show()