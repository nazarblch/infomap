function insert_slider(container_name, amount_name, min, max, cur, parent){

            var slider_el = parent.find( container_name );
            var amount_el = parent.find( amount_name );


            slider_el.slider({
                range: "min",
                value: cur,
                min: min,
                max: max,
                animate: true,
                slide: function( event, ui ) {
                    amount_el.val(ui.value );
                }

            });



            amount_el.val(slider_el.slider( "value" ) );

            amount_el.change(function() {
                slider_el.slider( "value" , parseInt(amount_el.val()) )
            });


            return slider_el;


}
