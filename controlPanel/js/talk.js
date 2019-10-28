

$(".btn-talk").click(function(){
    $(this).parent().find(".card-text").each(function() {
        var slots = {
            "lang" : "ja",
            "say_text" : this.textContent,
        }
        setSlots(slots, "action_nao_say_text");
    });
}); 