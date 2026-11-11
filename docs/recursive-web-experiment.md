# Recursive web -> basis experiment

## web
| round | sources | train_obs | defs | train_plan_steps | held_obs | held_plan_steps | held_rows | held_calls |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 2 | A+B | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| 3 | A+B+C | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| 4 | A+B+C+D | 2 | 2 | 2 | 0 | 2 | 0 | 1 |
| 5 | A+B+C+D+E | 2 | 2 | 2 | 0 | 2 | 0 | 1 |
| 6 | A+B+C+D+E+F | 2 | 2 | 2 | 1 | 2 | 6 | 1 |

## no-web
| round | sources | train_obs | defs | train_plan_steps | held_obs | held_plan_steps | held_rows | held_calls |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 2 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 3 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 4 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 5 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 6 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |

## single
| round | sources | train_obs | defs | train_plan_steps | held_obs | held_plan_steps | held_rows | held_calls |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 2 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 3 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 4 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 5 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 6 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |

## scrambled
| round | sources | train_obs | defs | train_plan_steps | held_obs | held_plan_steps | held_rows | held_calls |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 2 | A+B | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 3 | A+B+C | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 4 | A+B+C+D | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| 5 | A+B+C+D+E | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| 6 | A+B+C+D+E+F | 1 | 0 | 3 | 0 | 3 | 0 | 0 |

## frozen
| round | sources | train_obs | defs | train_plan_steps | held_obs | held_plan_steps | held_rows | held_calls |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | A | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| 2 | A+B | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| 3 | A+B+C | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| 4 | A+B+C+D | 2 | 0 | 3 | 0 | 3 | 0 | 0 |
| 5 | A+B+C+D+E | 2 | 0 | 3 | 0 | 3 | 0 | 0 |
| 6 | A+B+C+D+E+F | 2 | 0 | 3 | 1 | 3 | 6 | 0 |

