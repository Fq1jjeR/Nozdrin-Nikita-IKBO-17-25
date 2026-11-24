base_health is 100.0;
base_mana is 50.0;
level_bonus is 1.5;
critical_multiplier is 2.0;

{
  character -> {
    name -> 0.0.
    level -> 0.0.
    health -> .(base_health + level_bonus * 10.0).
    mana -> .(base_mana + level_bonus * 5.0).
  }.

  combat -> {
    attack -> .(base_health * 0.1 + base_mana * 0.2).
    defense -> .(base_health * 0.05).
    critical -> .(base_health * 0.1 * critical_multiplier).
  }.

  inventory -> {
    sword -> { damage -> 25.0. durability -> 100.0. }.
    shield -> { armor -> 15.0. durability -> 80.0. }.
    potion -> { count -> 5.0. heal -> .(base_health * 0.3). }.
  }.

  vision -> {
    range -> .(min(120.0, 150.0)).
    deviation -> .(abs(base_mana - 50.0)).
  }.
}
