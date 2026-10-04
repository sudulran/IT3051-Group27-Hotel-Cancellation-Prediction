# Final Model Input Schema

## Purpose

The saved `final_hotel_cancellation_pipeline.joblib` expects the finalized **32-column engineered model-input representation**. It does not directly accept arbitrary raw frontend fields.

During backend development, deterministic inference-time feature engineering must convert validated user/form inputs into exactly these columns and this column order before prediction.

The backend must call `pipeline.predict_proba(...)` and apply the probability threshold stored in `models/final_model_metadata.json`.

## Column contract

| Column | Role | Data type | Missing permitted | Allowed / observed values or notes |
|---|---|---|---|---|
| hotel | Categorical | string/category | No in finalized training data | Training-observed categories: City Hotel, Resort Hotel. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| lead_time | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 737. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| arrival_date_year | Numeric | numeric | No in finalized training data | Training-observed range: 2015 to 2017. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| arrival_date_month | Categorical | string/category | No in finalized training data | Training-observed categories: April, August, December, February, January, July, June, March, May, November, October, September. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| arrival_date_week_number | Numeric | numeric | No in finalized training data | Training-observed range: 1 to 53. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| arrival_date_day_of_month | Numeric | numeric | No in finalized training data | Training-observed range: 1 to 31. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| stays_in_weekend_nights | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 19. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| stays_in_week_nights | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 50. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| adults | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 55. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| children | Numeric — special imputation | numeric | Yes — most-frequent imputation in pipeline | Training-observed range: 0 to 10. RobustScaler applied after imputation. |
| babies | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 10. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| meal | Categorical | string/category | No in finalized training data | Training-observed categories: BB, FB, HB, SC, Undefined. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| country | Categorical | string/category | Yes — imputed to Unknown | 167 categories observed in training. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| market_segment | Categorical | string/category | No in finalized training data | Training-observed categories: Aviation, Complementary, Corporate, Direct, Groups, Offline TA/TO, Online TA, Undefined. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| distribution_channel | Categorical | string/category | No in finalized training data | Training-observed categories: Corporate, Direct, GDS, TA/TO, Undefined. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| is_repeated_guest | Binary | integer | No | Allowed model representation: 0 or 1. |
| previous_cancellations | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 26. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| previous_bookings_not_canceled | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 59. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| reserved_room_type | Categorical | string/category | No in finalized training data | Training-observed categories: A, B, C, D, E, F, G, H, L, P. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| deposit_type | Categorical | string/category | No in finalized training data | Training-observed categories: No Deposit, Non Refund, Refundable. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| customer_type | Categorical | string/category | No in finalized training data | Training-observed categories: Contract, Group, Transient, Transient-Party. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |
| adr | Numeric | numeric | No in finalized training data | Training-observed range: -6.38 to 5400. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| required_car_parking_spaces | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 8. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| total_of_special_requests | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 5. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| total_nights | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 69. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| total_guests | Numeric | numeric | No in finalized training data | Training-observed range: 0 to 55. RobustScaler applied. These observed ranges are documentation, not automatic hard limits for future backend validation. |
| has_children | Binary | integer | No | Allowed model representation: 0 or 1. |
| has_agent | Binary | integer | No | Allowed model representation: 0 or 1. |
| has_company | Binary | integer | No | Allowed model representation: 0 or 1. |
| is_zero_guest | Binary | integer | No | Allowed model representation: 0 or 1. |
| is_zero_night | Binary | integer | No | Allowed model representation: 0 or 1. |
| booking_month | Categorical | string/category | No in finalized training data | Training-observed categories: 1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9. Unseen values are accepted by OneHotEncoder(handle_unknown='ignore'). |

## Important deployment distinction

This schema documents the input expected by the fitted model pipeline **after deterministic feature engineering**. A future frontend should ask only for legitimate prediction-time inputs. The backend must derive engineered fields such as totals and binary indicators consistently with Notebook 02 before invoking the saved pipeline.

Outcome/leakage fields excluded during model development must never be introduced into the backend prediction request.
