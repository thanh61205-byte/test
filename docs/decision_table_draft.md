# Draft decision table — risk × value × time → action

Status: **C2 draft (provisional)**. It gives F a concrete target use case. Every threshold below is a placeholder to be set in F2/G1 from validation folds, staff capacity and costs. Nothing here is a tested rule, and no figure here is a result.

## 1. Inputs at decision time

| Input | Definition | Source |
|---|---|---|
| `p_cancel` | Calibrated cancellation probability | F model (`risk_scores`) |
| `value_at_risk` | `p_cancel` × booking contribution (`syn_net_booking_value`; gross value as a check) | F model + finance table (**simulated** inputs) |
| `days_to_arrival` | `arrival_date` − decision date | PMS |
| `population` | `individual` or `group_block` (inferred proxy, notebook 03 §2.0) | notebook 03 rule |
| Capacity | Calls / tasks the reservations team can handle per day | Reservations lead (to collect) |

## 2. Eligibility (applied before any rule)

A booking is considered only if **all** hold:
1. Status is active: not cancelled, not checked in, arrival date after the decision date.
2. It passes the data-quality rules (`exclude_from_model == False`); otherwise it goes to manual review.
3. It is not complimentary (`adr_clean == 0` in segment Complementary).
4. The guest has not opted out of non-essential contact, and no other open action of the same type exists for it.

## 3. Individual track (guest follow-up)

`t_low`, `t_high`, `N` and `D` are **provisional** placeholders.

| Rule | Condition | Action (`action_type`) | Owner | Approval | Limit / stop condition |
|---|---|---|---|---|---|
| I1 | `p_cancel < t_low` | Standard confirmation at booking + reminder 7 days before arrival (`confirm_email`, `reminder`) | n8n, monitored by Reservations | auto | Stop when the guest confirms or cancels |
| I2 | `t_low ≤ p_cancel < t_high` and `days_to_arrival ≥ 8` | Personalised reminder by email/SMS at 30 and 14 days before arrival; a booking that enters the band after a milestone has passed (e.g. at 8–13 days) gets one reminder **immediately**, then follows the remaining schedule (`reminder`) | n8n, monitored by Reservations | auto | Max 2 messages; stop on any response |
| I3 | `p_cancel ≥ t_high` and `days_to_arrival ≥ 8` | Phone call from the follow-up queue, ranked by `value_at_risk` (`phone_call`) | Reservations / front office | none (internal task) | At most `N` calls per day (capacity); max 2 attempts per booking; stop on response |
| I4 | I3 contact and the guest asks to change | Offer a date / room change (`offer_change`) | Reservations | **Revenue manager** if price or discount changes | One offer per booking |
| I5 | `p_cancel ≥ t_high` and `days_to_arrival ≤ 7` | No call (too late to change much); count the booking in the date × room-type cancellation buffer (feeds G2/G3) | Revenue manager | — | — |
| I6 | `p_cancel ≥ t_high`, No Deposit, high value, and policy allows | Ask for a deposit / guarantee (`request_deposit`) | Reservations | **Revenue manager** (significant effect on the guest, GDPR Art. 22 human review) | Off by default; only under a written policy |

**Priority when several rules match the same booking:** I5 (≤ 7 days) overrides I2/I3. Otherwise the strongest applicable action runs and weaker ones are suppressed: I6 (if policy allows and approved) > I3 > I2 > I1. I4 only follows an I3 contact. A booking never receives an automated reminder (I1/I2) on the same day as a phone call (I3).

## 4. Group / block track (capacity management)

| Rule | Condition | Action | Owner | Approval | Limit / stop condition |
|---|---|---|---|---|---|
| G1 | Block with release deadline within `D` days and low pickup | Ask the agent / tour operator to confirm or release rooms | Distribution / sales | Revenue manager for the release decision | Contract terms |
| G2 | Forecast released rooms for a date × room type above the buffer | Reallocate capacity and put rooms back on sale (`capacity_allocation`, `resale`) | Revenue manager | **Required** | Never sell more than the rooms actually released |
| G3 | High forecast cancellations and high demand on a date × room type | Controlled overbooking (`overbooking`) | Revenue manager | **Required (GM for limits)** | Provisional limit per room type and night; stop if relocations occur |
| G4 | New group contract with a history of large releases | Staged deposits / earlier release dates | Distribution / sales + Finance | **Required** | Contract negotiation |
| G5 | Price change for a date × room type driven by the buffer | `price_adjustment` | Revenue manager | **Required** | Within the hotel's rate rules |

## 5. Programme-level stop conditions

- Pause automated messages if complaints or opt-outs exceed a level agreed with CX.
- The pilot runs with a **randomised holdout**: eligible bookings are assigned to `treatment` or `holdout` before any action and recorded in `pilot_assignment` (stratified by risk tier). Effects are measured **by assigned arm** (intention to treat), never by comparing only the guests actually contacted (KPIs C1, B6). If no positive uplift is seen after the agreed pilot length, stop or redesign the rules; do not scale.
- Intervention cost per month stays within the budget set by Finance (KPI B7).

## 6. Approval guard (specification for G2)

The schema **records** approvals (`action_plan.needs_approval`, `approval_status`, `approved_by`); it does not yet **enforce** them. G2 must implement and test:

1. `needs_approval = TRUE` for `request_deposit`, `price_adjustment`, `capacity_allocation`, `resale`, `overbooking`, and for `offer_change` with a price change. For these actions, `approval_status` can never be `auto`.
2. An `interventions` row may be written **only if** its action has `approval_status IN ('auto', 'approved')`. Enforce this in the n8n/service layer **and** with a database check (trigger on `interventions` insert), so neither layer can be bypassed alone.
3. Rejected or pending actions are never executed; every approval or rejection stores who decided (`approved_by`) and when (`approved_at`). The schema already rejects an `auto` status on an action that needs approval and an approval without `approved_by` / `approved_at` (CHECK constraints on `action_plan`).
4. Tests: inserting an intervention for a `pending` or `rejected` action must fail; an approved action must pass; an `auto` action with `needs_approval = TRUE` must be impossible.

## 7. Owners (stakeholders)

| Stakeholder | Owns |
|---|---|
| General manager | Programme approval, overbooking limits, budget |
| Revenue manager | Thresholds, capacity / price / resale / overbooking decisions, approvals, business KPIs B1–B5 and B9 |
| Reservations / front office | Follow-up queue, contacts, process KPIs P1–P2 |
| Customer service / CX | Message content, opt-outs, CX KPIs C1–C2 |
| Finance | Cost and contribution assumptions, KPIs B6–B7 |
| Distribution / sales | Agents and tour operators, block contracts, KPI B8 |
| Data / analytics team | Model, calibration, model KPIs M1–M6, monitoring |
| Guests | Affected party: receive the interventions; transparency in the privacy notice |
