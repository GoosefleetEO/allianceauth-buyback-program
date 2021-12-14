$(function () {
  $("#id_item_type").autoComplete({
    resolverSettings: {
      url: "/buybackprogram/item_autocomplete/",
    },
  });
});
