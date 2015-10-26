var fetchRecords = function(input) {
    var searchTerm = input.value;
    doSearch(searchTerm);
};

var noResults = function(){
    $("#results").show();
    $("#loading").hide();
    $('#count span').text('0');
    $('#premises-list').empty();
};

var doSearch = function(searchTerm) {
    $("#results").hide();
    $("#loading").show();
    $.ajax({
      type: 'GET',
      url: "/search?query="+searchTerm,
      success: function(data) {
        $('#premises-list').empty();
        $("#loading").hide();
        $("#results").show();
        if(searchTerm.length == 0){
          $('#count span').text(data.meta.total_entries);
        } else {
          $('#count span').text(data.entries.length);
        }
        var template = $.templates("#premises-template");
        $.each(data.entries, function(index, item) {
            var html = template.render({
                'premisesId': item.entry.premises,
                'premisesName': item.entry.name
            });
            $('#premises-list').append(html);
        });
      },
      error: function(XMLHttpRequest, textStatus, errorThrown) {
        console.log('status:' + XMLHttpRequest.status + ', status text: ' + XMLHttpRequest.statusText);
        noResults();
      },
    });
};


var pager = function(event) {
  event.preventDefault();
  var searchTerm = $('#search')[0].value,
    page = $('#page-number').text();
  $.ajax({
    type: 'GET',
    url: "/search?query="+searchTerm+"&page="+page,
    success: function(data) {
      $('#premises-list').empty();
      $('#page-number').text(data.meta.page+1);

      if(searchTerm.length == 0){
        $('#count span').text(data.meta.total_entries);
      } else {
        $('#count span').text(data.entries.length);
      }

      var template = $.templates("#premises-template");
      $.each(data.entries, function(index, item) {
          var html = template.render({
              'premisesId': item.entry.premises,
              'premisesName': item.entry.name
          });
          $('#premises-list').append(html);
      });
    },
    error: function(){
      console.log("error");
    }
  });
};


$(document).ready(function() {
    $('#search').on('keyup', function(event) {
      fetchRecords(event.currentTarget);
    });
    $('#pager').on('click', pager);
});
