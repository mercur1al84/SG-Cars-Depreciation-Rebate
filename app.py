import streamlit as st
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import math

st.title("Depreciation & Paper Rebate Calculator")

vehicle_model = st.text_input("Vehicle Model", placeholder="e.g. Toyota Altis 1.6 Elegance")

handover_date = st.date_input(
    "Handover Date of Car",
    value=date.today(),
    min_value=date(1970, 1, 1),
    format="DD/MM/YYYY"
)

current_price = st.number_input("Purchase Price ($)", value=80000)

reg_date = st.date_input(
    "Original Registration Date",
    value=date(2020, 1, 1),
    min_value=date(1970, 1, 1),
    max_value=date.today(),
    format="DD/MM/YYYY"
)

arf = st.number_input("ARF (Additional Registration Fee) ($)", value=30000)
coe_bidding_price = st.number_input("COE ($)", value=50000)

is_renewed = st.checkbox("Car is COE Renewed")

if is_renewed:
    coe_renewal_value = st.number_input("COE Paid at Renewal ($)", value=40000)
    coe_expiry_date = st.date_input(
        "COE Expiry Date",
        value=date(2033, 1, 1),
        min_value=date.today(),
        max_value=date.today() + timedelta(days=365 * 20),
        format="DD/MM/YYYY"
    )
else:
    coe_renewal_value = 0
    coe_expiry_date = None

override_arf_cap = st.checkbox(
    "Override ARF cap of $60,000 (For cars registered after 22nd Feb 2023 using COE obtained from earlier biddings)"
)

arf_cap_start = datetime.strptime("22/02/2023", "%d/%m/%Y").date()

def diff_years_months_days(start_date, end_date):
    diff = relativedelta(end_date, start_date)
    return diff.years, diff.months, diff.days

if is_renewed:
    if coe_expiry_date is None:
        st.error("Please enter the COE Expiry Date.")
    else:
        remaining_days = (coe_expiry_date - handover_date).days
        remaining_coe_years = max(0.01, remaining_days / 365)

        annual_depreciation = current_price / remaining_coe_years

        residual_coe_value = math.floor(coe_renewal_value * (remaining_days / 3650))

        tiered_arf_rebate = 0
        final_arf_rebate = 0

        remaining_y, remaining_m, remaining_d = diff_years_months_days(handover_date, coe_expiry_date)

else:
    car_age_days = (handover_date - reg_date).days
    car_age_years_float = car_age_days / 365
    remaining_coe_years_float = max(0.01, 10 - car_age_years_float)
    coe_expiry_date = reg_date.replace(year=reg_date.year + 10) - timedelta(days=1)

    # Tiered ARF rebate at handover
    if car_age_years_float <= 5:
        tier_pct = 0.75
    elif car_age_years_float <= 6:
        tier_pct = 0.70
    elif car_age_years_float <= 7:
        tier_pct = 0.65
    elif car_age_years_float <= 8:
        tier_pct = 0.60
    elif car_age_years_float <= 9:
        tier_pct = 0.55
    elif car_age_years_float <= 10:
        tier_pct = 0.50
    else:
        tier_pct = 0.0

    calculated_rebate = arf * tier_pct

    if reg_date >= arf_cap_start and not override_arf_cap:
        if calculated_rebate > 60000:
            st.warning("⚠️ ARF rebate capped at $60,000 for cars registered on or after 22/02/2023.")
        tiered_arf_rebate = min(calculated_rebate, 60000)
    else:
        tiered_arf_rebate = calculated_rebate

    tiered_arf_rebate = math.floor(tiered_arf_rebate)

    # Residual COE paper value
    residual_coe_value = math.floor(coe_bidding_price * (remaining_coe_years_float / 10))

    # Final ARF rebate at 10 years
    final_arf_rebate = 0.5 * arf
    if reg_date >= arf_cap_start and not override_arf_cap:
        if final_arf_rebate > 60000:
            st.warning("⚠️ Final ARF rebate capped at $60,000 for cars registered on or after 22/02/2023.")
        final_arf_rebate = min(final_arf_rebate, 60000)

    final_arf_rebate = math.floor(final_arf_rebate)

    depreciation_total = current_price - final_arf_rebate
    annual_depreciation = depreciation_total / remaining_coe_years_float

    remaining_y, remaining_m, remaining_d = diff_years_months_days(handover_date, coe_expiry_date)
    car_age_y, car_age_m, car_age_d = diff_years_months_days(reg_date, handover_date)

# Final Paper Rebate
paper_rebate = tiered_arf_rebate + residual_coe_value

# -------------------- RESULTS --------------------
st.subheader("Results")

if vehicle_model:
    st.write(f"**Vehicle Model:** {vehicle_model}")

if is_renewed and coe_expiry_date:
    st.write(f"COE Expiry Date: {coe_expiry_date.strftime('%d/%m/%Y')}")
    st.write(f"Remaining COE: {remaining_y} years, {remaining_m} months, {remaining_d} days")
    st.write(f"Residual COE Value: ${residual_coe_value:,}")
else:
    st.write(f"Original Registration Date: {reg_date.strftime('%d/%m/%Y')}")
    st.write(f"Handover Date: {handover_date.strftime('%d/%m/%Y')}")
    st.write(f"COE Expiry Date: {coe_expiry_date.strftime('%d/%m/%Y')}")
    st.write(f"Car Age: {car_age_y} years, {car_age_m} months, {car_age_d} days")
    st.write(f"Remaining COE: {remaining_y} years, {remaining_m} months, {remaining_d} days")
    st.write(f"Tiered ARF Rebate: ${tiered_arf_rebate:,}")
    st.write(f"Residual COE Value: ${residual_coe_value:,}")

st.write(f"**Paper Rebate as at Handover of Vehicle: ${paper_rebate:,}**")
st.write(f"**Annual Depreciation: ${annual_depreciation:,.2f} / year**")

st.markdown("<p style='text-align: center; color: grey;'>© 2025 Aztute Automotive Pte Ltd</p>", unsafe_allow_html=True)
