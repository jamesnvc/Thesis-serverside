/* Author: James Cash

*/
$(document).ready(function() {
    $('#analyze').click(function() {
        var tracks = $('.track-chooser select').map(function() {
            return this.value;
        }).get().join('-');
        jQuery.ajax('/analyze', {
          data: {tracks: tracks},
          type: 'POST',
          success: function(data, status, xhr) {
            $('.results').removeClass('error').addClass('success').html(data);
          },
          error: function(xhr, status, err) {
            $('.results').
              removeClass('error').
              addClass('error').
              text("Error: "+ status);
          }
        });
    });
});
