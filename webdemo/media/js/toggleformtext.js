
$.fn.addsuggest = function() {

    this.each(function(){
        if(this.value == '')
            this.value = this.title;
    });

    this.focus(function(){
        if(this.value == this.title)
            this.value = '';
    });

    this.blur(function(){
        if(this.value == '')
            this.value = this.title;
    });

    this.parents("form").find("input:image, input:button, input:submit").click(function(){
        $(this.form.elements).each(function(){
            if(this.type =='text' || this.type =='textarea' || this.type =='password' ){
                if(this.value == this.title && this.title != ''){
                    this.value='';
                }
            }
        });
    });
};