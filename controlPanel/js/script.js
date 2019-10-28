
function navnext( next ) {
    $( ":mobile-pagecontainer" ).pagecontainer( "change", next, {
        transition: "slide"
    });
}
function navprev( prev ) {
    $( ":mobile-pagecontainer" ).pagecontainer( "change", prev, {
        transition: "slide",
        reverse: true
    });
}

function getHashFromUrl(url){
    var pageId = $("<a />").attr("href", url)[0].hash.replace(/^#/, "");
    if (pageId != ""){
        return pageId;
    }
    return "naotalk";
}

$( document ).one( "pagecreate", "#" + getHashFromUrl(window.location.href), function() {
    // Handler for navigating to the next page
    // Navigate to the next page on swipeleft
    $( document ).on( "swipeleft", ".ui-page", function( event ) {
        // Get the filename of the next page. We stored that in the data-next
        // attribute in the original markup.
        var next = $( this ).jqmData( "next" );
        if ( next ) {
            navnext( next );
        }
    });
    // The same for the navigating to the previous page
    $( document ).on( "swiperight", ".ui-page", function( event ) {
        var prev = $( this ).jqmData( "prev" );
        if (prev) {
            navprev( prev );
        }
    });

    $( document ).on('pagebeforeshow', function() {
        if ($.mobile.activePage.attr('id') == "naoconfig"){
            $.ajax({
                type: "GET",
                url: langChangeUrl,
                success: function(response){
                    $("#chatBoxLang").val(response['lang']);
                    $("#chatBoxLang-button .ui-selectmenu-button-text").text($("#chatBoxLang :selected").text());
                    startRecognition(response['lang']);
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    console.log(xhr.status);
                    console.log(thrownError);
                }
            });
        } else {
            if (typeof recognition  !== "undefined"){
                recognition.stop();
                stopRecog = true;
            }
        }
    });
});
