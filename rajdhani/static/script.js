const autocompleteURL = "/api/stations";
const searchURL = "/api/search";

function getQuerystring(obj) {
  return Object.entries(obj)
    .map((kv) => kv.map(encodeURIComponent))
    .map(([k, v]) => `${k}=${v}`)
    .join("&");
}

async function getAutocomplete(input) {
  const qs = getQuerystring({ q: input });
  const url = `${autocompleteURL}?${qs}`;

  const response = await fetch(url);
  const stations = await response.json();

  return stations.map(({ code, name }) => {
    return {
      value: code,
      text: `${name} - ${code}`,
    };
  });
}

async function searchTrains(from, to, ticketClass) {
  const qs = getQuerystring({ from,  to, class: ticketClass })
  const url = `${searchURL}?${qs}`

  const response = await fetch(url)
  const trains = await response.json()

  return trains
}

function selectFromStation(value, text) {
  $("#from-station-text").val(text);
  $("#from-station").val(value);
}

function selectToStation(value, text) {
  $("#to-station-text").val(text);
  $("#to-station").val(value);
}

function refreshAutocomplete(input, $list) {
  getAutocomplete(input)
    .then((stations) => {
      let html = stations
        .map(({ value, text }) => getAutocompleteItem(value, text))
        .join("\n");

      $list.html(
        stations
          .map(({ value, text }) => getAutocompleteItem(value, text))
          .join("\n")
      );
    })
    .catch((error) => {
      console.error(error);
    });
}

function getAutocompleteItem(value, text) {
  return `
        <li class="autocomplete-item" data-value="${value}">
            ${text}
        </li>`;
}


$(document).ready(function () {
  const $fromStationDiv = $("#from-station-div");
  const $toStationDiv = $("#to-station-div");
  const $fromList = $("#from-station-autocomplete-items");
  const $toList = $("#to-station-autocomplete-items");
  const $fromText = $("#from-station-text");
  const $toText = $("#to-station-text");

  $fromText.keyup(function () {
    const input = $(this).val();
    refreshAutocomplete(input, $fromList);
  });

  $toText.keyup(function () {
    const input = $(this).val();
    refreshAutocomplete(input, $toList);
  });

  $fromText.focusin(function () {
    $fromList.show();
  });

  $fromStationDiv.focusout(function (e) {
    $fromList.hide();
  });

  $toText.focusin(function () {
    $toList.show();
  });

  $toStationDiv.focusout(function () {
    $toList.hide();
  });

  $(".autocomplete-list").on("mousedown", ".autocomplete-item", function () {
    let text = $(this).text().trim();
    let { value } = $(this).data();
    value = value.trim()

    const $list = $(this).parent();
    let { valueTarget, textTarget } = $list.data();

    $(valueTarget).val(value);
    $(textTarget).val(text);
  });
});
