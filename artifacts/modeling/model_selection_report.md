# Model evaluation report

## Scope and caveats
- Selected model: **logistic_regression**.
- Final fit: all train + validation rows through 2016-12-31; test begins 2017-01-01.
- Validation and test were previously inspected in notebook 03 EDA; test is not historically untouched.
- Dataset is a near-arrival snapshot; results are retrospective and not a production performance guarantee.
- Frozen threshold: **0.234928**, selected on validation to maximize recall subject to alert share <= 20%.
- Capacity fallback used: **False**.

## Validation model comparison
                 model  validation_pr_auc  validation_event_rate_baseline  validation_roc_auc  validation_brier  validation_brier_uncalibrated  threshold  precision   recall       f1    tn   fp   fn   tp  alert_share  alerts_in_cohort  queue_per_1000  cv_pr_auc_mean  cv_pr_auc_std  capacity_eligible  selected
   logistic_regression           0.457311                        0.314821            0.686271          0.220159                       0.201016   0.234928   0.464105 0.294798 0.360566  8576 1590 3294 1377     0.199973              2967      199.973040        0.528067       0.193100               True      True
         random_forest           0.424237                        0.314821            0.656683          0.219471                       0.215004   0.262106   0.437816 0.278099 0.340141  8498 1668 3372 1299     0.199973              2967      199.973040        0.546899       0.181649               True     False
               xgboost           0.418093                        0.314821            0.648093          0.221841                       0.227319   0.261686   0.418354 0.265468 0.324820  8442 1724 3431 1240     0.199771              2964      199.770843        0.544121       0.163338               True     False
hist_gradient_boosting           0.419281                        0.314821            0.648653          0.214118                       0.227935   0.282327   0.425776 0.270178 0.330583  8464 1702 3409 1262     0.199771              2964      199.770843        0.542088       0.183334               True     False
     baseline_logistic           0.427882                        0.314821            0.657693          0.203555                       0.203647   0.398007   0.443466 0.280454 0.343607  8522 1644 3361 1310     0.199097              2954      199.096852        0.345203       0.012624               True     False
   constant_event_rate           0.314821                        0.314821            0.500000          0.219770                       0.219770   1.000001   0.000000 0.000000 0.000000 10166    0 4671    0     0.000000                 0        0.000000             NaN            NaN               True     False

## Test evaluation (single final evaluation)
              model  threshold_frozen_from_validation  test_rows  test_event_rate_baseline  test_pr_auc  test_roc_auc  test_brier  test_brier_uncalibrated calibration  precision  recall       f1   tn   fp  fn   tp  alert_share  alerts_in_cohort  queue_per_1000
logistic_regression                          0.234928      20399                  0.343742     0.528857      0.720381    0.205936                 0.195196     sigmoid   0.452085 0.87664 0.596535 5937 7450 865 6147     0.666552             13597      666.552282

## Selection rule
Prefer candidates meeting alert capacity; among them take the validation AP leader and retain candidates within 0.01 AP. Tie-break by temporal CV mean AP, lower fold variability, higher recall then precision at capacity, lower Brier, then simplicity/reproducibility (LR, HGB, RF, XGBoost). Constant event-rate baseline is reference only. No model is selected solely by CV.

## Interpretation checklist
- Compare PR-AUC with event-rate baseline; report ROC-AUC and Brier alongside threshold metrics.
- Review precision/recall, confusion matrix, alert share and expected queue per 1,000.
- Inspect market-segment and lead-time-band subgroup table; small groups (<100) are omitted. Lead-time groups are diagnostic until as-of validity is confirmed.
- Permutation importance is validation-based and associative, not causal.
- Verify as-of feature availability, calibration drift, operational capacity and false-positive/false-negative costs before deployment.


## Temporal CV results

                 model  cv_pr_auc_mean  cv_pr_auc_std  cv_pr_auc_min  cv_pr_auc_max                                                                                                                                                                                                                  best_params  fold_1_pr_auc  fold_2_pr_auc  fold_3_pr_auc  fold_4_pr_auc
   logistic_regression        0.528067       0.193100       0.383503       0.812842                                                                                                                                                                              {"C": 86.78162918126168, "solver": "liblinear"}       0.812842       0.383503       0.453639       0.462285
         random_forest        0.546899       0.181649       0.422675       0.813593                                                                                                                                        {"n_estimators": 600, "max_depth": 17, "min_samples_leaf": 9, "max_features": "sqrt"}       0.813593       0.441880       0.509447       0.422675
               xgboost        0.544121       0.163338       0.437986       0.785346 {"n_estimators": 300, "max_depth": 8, "learning_rate": 0.02758409553341385, "subsample": 0.8448187640719614, "colsample_bytree": 0.813128080244132, "min_child_weight": 10.749774708730362, "reg_lambda": 2.534381560762948}       0.785346       0.437986       0.503594       0.449560
hist_gradient_boosting        0.542088       0.183334       0.414772       0.811873                                                                              {"max_iter": 300, "learning_rate": 0.025869008902851338, "max_leaf_nodes": 28, "l2_regularization": 1.4539538247902701, "min_samples_leaf": 35}       0.811873       0.414772       0.499942       0.441766
     baseline_logistic        0.345203       0.012624       0.328066       0.357676                                                                                                                                                                                                                           {}       0.357676       0.350534       0.344534       0.328066

## Validation subgroup metrics

  segment_type       segment     n  event_rate   pr_auc  roc_auc  precision   recall  alert_share  alerts_in_group  queue_per_1000
market_segment Complementary   125    0.088000 0.163765 0.595295   0.333333 0.090909     0.024000                3       24.000000
market_segment     Corporate   570    0.098246 0.144855 0.562517   0.200000 0.035714     0.017544               10       17.543860
market_segment        Direct  1404    0.200142 0.252762 0.565942   0.278689 0.060498     0.043447               61       43.447293
market_segment Offline TA/TO  1850    0.143243 0.202307 0.602103   0.305556 0.041509     0.019459               36       19.459459
market_segment     Online TA 10827    0.373511 0.478491 0.642910   0.471103 0.332591     0.263693             2855      263.692620
lead_time_band          0-7d  2179    0.117944 0.182545 0.585108   0.500000 0.007782     0.001836                4        1.835704
lead_time_band         8-30d  2649    0.278218 0.411406 0.664255   0.465035 0.180461     0.107965              286      107.965270
lead_time_band        31-90d  4312    0.339981 0.438693 0.649591   0.439960 0.297408     0.229824              991      229.823748
lead_time_band       91-180d  3664    0.381004 0.465520 0.617324   0.455157 0.436246     0.365175             1338      365.174672
lead_time_band         180d+  2033    0.400885 0.569880 0.689094   0.566092 0.241718     0.171176              348      171.175603

## Top validation permutation importance

             feature  importance_mean  importance_std
           agent_top         0.110052        0.001669
       lead_time_log         0.048854        0.002200
       customer_type         0.019050        0.001603
   prev_cancel_ratio         0.012292        0.001724
      is_high_season         0.010099        0.000343
        is_long_stay         0.007801        0.000620
stays_in_week_nights         0.007266        0.000621
      is_last_minute         0.005751        0.001591
             is_solo         0.005658        0.001295
                meal         0.005657        0.001004
        total_nights         0.005400        0.000608
    arrival_week_cos         0.005106        0.000275
        has_children         0.004459        0.001013
            children         0.002369        0.002071
        is_far_ahead         0.002157        0.000246


## Lift@k, bootstrap CI và so sánh với rule đơn giản

Block bootstrap theo tuần đến, 500 lần; CI 95%. Rule fit trên dữ liệu cùng cohort huấn luyện.

### Validation

scorer               rule_lead_time rule_segment_x_leadband        selected_model
metric                                                                           
lift@10%       1.325 [1.145, 1.484]    1.254 [1.159, 1.353]  1.537 [1.458, 1.641]
lift@20%       1.254 [1.164, 1.342]    1.249 [1.195, 1.332]  1.475 [1.393, 1.555]
lift@5%        1.357 [1.053, 1.584]    1.289 [1.169, 1.406]  1.614 [1.497, 1.757]
pr_auc         0.383 [0.351, 0.420]    0.396 [0.377, 0.419]  0.457 [0.438, 0.482]
precision@10%  0.417 [0.349, 0.484]    0.395 [0.362, 0.432]  0.484 [0.461, 0.517]
precision@20%  0.395 [0.358, 0.438]    0.393 [0.372, 0.425]  0.464 [0.440, 0.493]
precision@5%   0.427 [0.325, 0.509]    0.406 [0.368, 0.452]  0.508 [0.471, 0.551]
recall@10%     0.133 [0.114, 0.148]    0.125 [0.116, 0.135]  0.154 [0.146, 0.164]
recall@20%     0.251 [0.233, 0.269]    0.250 [0.239, 0.266]  0.295 [0.279, 0.311]
recall@5%      0.068 [0.053, 0.079]    0.064 [0.058, 0.070]  0.081 [0.075, 0.088]
roc_auc        0.610 [0.590, 0.630]    0.638 [0.625, 0.654]  0.686 [0.671, 0.704]

    cohort             model_minus        metric     diff    ci_low  ci_high  ci_excludes_0  boot_n
validation          rule_lead_time        pr_auc 0.074681  0.042943 0.102529           True     500
validation          rule_lead_time       roc_auc 0.076334  0.057553 0.095032           True     500
validation          rule_lead_time precision@10% 0.066712 -0.000080 0.140772          False     500
validation          rule_lead_time precision@20% 0.069407  0.027003 0.107750           True     500
validation          rule_lead_time      lift@10% 0.211903 -0.000270 0.460935          False     500
validation          rule_lead_time      lift@20% 0.220465  0.083441 0.355883           True     500
validation          rule_lead_time    recall@20% 0.044102  0.016689 0.071184           True     500
validation rule_segment_x_leadband        pr_auc 0.061249  0.047555 0.079056           True     500
validation rule_segment_x_leadband       roc_auc 0.048029  0.037004 0.060361           True     500
validation rule_segment_x_leadband precision@10% 0.088949  0.053739 0.135977           True     500
validation rule_segment_x_leadband precision@20% 0.071092  0.034214 0.098739           True     500
validation rule_segment_x_leadband      lift@10% 0.282538  0.168294 0.430093           True     500
validation rule_segment_x_leadband      lift@20% 0.225816  0.108241 0.314903           True     500
validation rule_segment_x_leadband    recall@20% 0.045172  0.021651 0.062988           True     500

### Test

scorer                  final_model        rule_lead_time rule_segment_x_leadband
metric                                                                           
lift@10%       1.680 [1.610, 1.768]  1.550 [1.449, 1.644]    1.610 [1.524, 1.678]
lift@20%       1.588 [1.526, 1.644]  1.360 [1.301, 1.430]    1.473 [1.419, 1.532]
lift@5%        1.714 [1.611, 1.828]  1.708 [1.556, 1.835]    1.577 [1.461, 1.696]
pr_auc         0.529 [0.512, 0.547]  0.450 [0.429, 0.472]    0.468 [0.451, 0.487]
precision@10%  0.577 [0.553, 0.603]  0.533 [0.491, 0.576]    0.553 [0.523, 0.583]
precision@20%  0.546 [0.525, 0.566]  0.467 [0.447, 0.498]    0.506 [0.483, 0.531]
precision@5%   0.589 [0.558, 0.622]  0.587 [0.532, 0.638]    0.542 [0.500, 0.586]
recall@10%     0.168 [0.161, 0.177]  0.155 [0.145, 0.164]    0.161 [0.152, 0.168]
recall@20%     0.318 [0.305, 0.329]  0.272 [0.260, 0.286]    0.295 [0.284, 0.306]
recall@5%      0.086 [0.081, 0.091]  0.085 [0.078, 0.092]    0.079 [0.073, 0.085]
roc_auc        0.720 [0.708, 0.731]  0.628 [0.614, 0.644]    0.678 [0.663, 0.693]

cohort             model_minus        metric     diff    ci_low  ci_high  ci_excludes_0  boot_n
  test          rule_lead_time        pr_auc 0.079013  0.056058 0.101585           True     500
  test          rule_lead_time       roc_auc 0.092226  0.078439 0.106291           True     500
  test          rule_lead_time precision@10% 0.044608 -0.002286 0.094420          False     500
  test          rule_lead_time precision@20% 0.078431  0.047889 0.105666           True     500
  test          rule_lead_time      lift@10% 0.129771 -0.006752 0.275894          False     500
  test          rule_lead_time      lift@20% 0.228169  0.137914 0.305225           True     500
  test          rule_lead_time    recall@20% 0.045636  0.027586 0.061045           True     500
  test rule_segment_x_leadband        pr_auc 0.061047  0.047399 0.075083           True     500
  test rule_segment_x_leadband       roc_auc 0.042868  0.033582 0.053220           True     500
  test rule_segment_x_leadband precision@10% 0.024020 -0.004895 0.063830          False     500
  test rule_segment_x_leadband precision@20% 0.039461  0.015601 0.064982           True     500
  test rule_segment_x_leadband      lift@10% 0.069877 -0.014097 0.185878          False     500
  test rule_segment_x_leadband      lift@20% 0.114798  0.044525 0.187971           True     500
  test rule_segment_x_leadband    recall@20% 0.022961  0.008906 0.037599           True     500
