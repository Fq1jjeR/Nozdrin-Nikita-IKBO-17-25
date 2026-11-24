base_port is 5430.0;
max_connections is 100.0;
memory_per_connection is 8.0;
reserve_ratio is 0.15;

{
  database -> {
    host -> 0.0.
    port -> base_port.
    name -> 0.0.
    timeout -> .(base_port * 0.1).
  }.

  pool -> {
    min_size -> .(max_connections * 0.1).
    max_size -> max_connections.
    reserve -> .(max_connections * reserve_ratio).
  }.

  limits -> {
    memory_mb -> .(max_connections * memory_per_connection).
    cpu_quota -> .(max_connections * 0.05).
    max_query_time -> .(base_port * 0.2).
  }.
}
