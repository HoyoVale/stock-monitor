import pandas as pd
from app.services.indicator_service import IndicatorService


def test_rsi_known_values():
    close_prices = [
        44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10,
        45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28,
    ]
    df = pd.DataFrame({"close": close_prices})
    svc = IndicatorService()
    result = svc.calc_rsi(df, period=14)
    assert abs(result["value"] - 70.53) < 0.1
