$(function () {
  $("#id_eve_solar_system").autoComplete({
    resolverSettings: {
      url: "/buybackprogram/solarsystem_autocomplete/",
    },
  });
});
