$(function () {
  $("#id_item_type").autoComplete({
    resolverSettings: {
      url: "/buybackprogram/item_autocomplete/",
    },
  });
$("#id_eve_solar_system").autoComplete({
    resolverSettings: {
      url: "/buybackprogram/solarsystem_autocomplete/",
    },
  });
});
