$(document).ready(function () {
    $(function () { 
        //Add text editor
        //$("#compose-textarea").wysihtml5();
        CKEDITOR.addCss('.cke_editable p { margin: 0 !important; }');
        CKEDITOR.replace('compose_textarea');  
        CKEDITOR.config.extraPlugins = 'justify, lineheight, font, liststyle, colorbutton, indentblock, textindent';
        CKEDITOR.addStylesSet('default',[
                {name :'Roman',element:'ol',attributes:{type:'I'}}
                ]);
        //Getting the value of ckeditor
        //var editor_data = CKEDITOR.instances.compose_textarea.getData();
        //console.log(editor_data);
        
    }); 
});