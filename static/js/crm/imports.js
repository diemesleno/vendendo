function open_import() {
  var modal = $('#dialogModal');
  modal.find('.modal-title').text('Importar Clientes');
  // Initialize file
  $('#file').val('');
  // Initialize content
  var body = "<div style='text-align:center;'>Se desejar, <a href='/static/common/arquivo_exemplo_cliente.xlsx'>baixe o arquivo exemplo</a>.</div>";
  body += "<label for='contact_name' class='control-label'>Arquivo:</label>";
  body += "<input type='file' class='form-control' id='file' value=''>";
  $('#container_form_import').html(body);
  $('#btn_import').prop('disabled', false);
  // show modal
  modal.modal('show');
}

function import_customers() {
  var csrfmiddlewaretoken = $('[name=csrfmiddlewaretoken]').val();
  var file = $("#file")[0].files[0];
  var fd = new FormData();
  fd.append('file_upload', file);
  fd.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
  $('#btn_import').prop('disabled', true);
  var body = "<div style='text-align:center;'>Processando, aguarde ...</div>"
  body += "<div style='text-align:center;'><img src='/static/images/hourglass.gif' width='64' height='64'></div>";
  $('#container_form_import').html(body);

  $.ajax({
    url: '/customer/import/',
    type: 'POST',
    data: fd,
    dataType: 'json',
    mimeType:"multipart/form-data",
    contentType: false,
    cache: false,
    processData:false,
    success: function(data) {
      console.log(data);
      if(data){
        if(data.imported){
          location.reload();
        }else{
          var body = "<div style='text-align:center;'><div class='panel panel-danger'>";
          body += "<div class='panel-heading'><h2 class='panel-title'>Ops! Ocorreu um problema</h2></div>";
          body += "<div class='panel-content'><ul>";
          for(i=0;i<data.messages.length;i++){
            console.log(data.messages.length);
            body += "<li>" + data.messages[i].message;
            if(data.messages[i].line != ''){
              body += " (linha " + data.messages[i].line + ")";
            }
            body += "</li>";
          }
          body += "</ul></div></div></div>";
        }
      }else{
        var body = "<div style='text-align:center;'><div class='panel panel-danger'>";
        body += "<div class='panel-heading'><h2 class='panel-title'>Ops! Ocorreu um problema</h2></div>";
        body += "<div class='panel-content'>O servidor não respondeu. Tente novamente.";
        body += "</div></div></div>";
      }
      $('#container_form_import').html(body);
    },
      statusCode: {
        500: function() {
          var body = "<div style='text-align:center;'><div class='panel panel-danger'>";
          body += "<div class='panel-heading'><h2 class='panel-title'>Ops! Ocorreu um problema</h2></div>";
          body += "<div class='panel-content'>Erro interno";
          body += "</div></div></div>";
          $('#container_form_import').html(body);
        }
      }
  });
}