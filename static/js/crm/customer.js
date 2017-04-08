function get_new_idx() {
  if($('#table_body input').length > 0) {
    var _last_id = 0;
    $.each($('#table_body tr'), function(i, val) {
      _id = $(val).attr('id').split('_')[1];
      if(parseInt(_id) > parseInt(_last_id)) {
        _last_id = _id;
      }
    });
    return parseInt(_last_id) + 1;
  }else{
    return 1;
  }
}

$('#btn_add').click(function(){
  if(validate_form()) {
    var _contact_name = $('#contact_name').val();
    var _contact_email = $('#contact_email').val();
    var _contact_tel = $('#contact_tel').val();
    var _contact_position = $('#contact_position').val();
    var html_body = $('#table_body').html();
    var _idx = get_new_idx();
    var html_new_line = "<tr id=\"contact_"+_idx+"\"><input type='hidden' id='contact_name_contact_"+_idx+"' name='contact_name' value='"+_contact_name+"'><input type='hidden' id='contact_email_contact_"+_idx+"' name='contact_email' value='"+_contact_email+"'><input type='hidden' id='contact_tel_contact_"+_idx+"' name='contact_tel' value='"+_contact_tel+"'><input type='hidden' id='contact_position_contact_"+_idx+"' name='contact_position' value='"+_contact_position+"'><td style=\"width:70px;\"><button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:RemoveContact('contact_"+_idx+"');\"><span class='glyphicon glyphicon-trash' aria-hidden='true'></span></button> <button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:EditContact('contact_"+_idx+"');\"><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></button></td><td>"+_contact_name+"</td><td>"+_contact_email+"</td><td>"+_contact_tel+"</td><td>"+_contact_position+"</td></tr>";
    // Add line
    if($('#table_body input').length > 0) {
      html_body = html_body + html_new_line;
    }else{
      html_body = html_new_line;
    }
    
    $('#table_body').html(html_body);
    $('#dialogModal').modal('hide');
  }
});

$('#btn_save').click(function(){
  if(validate_form()) {
    var _edit_contact_id = $('#edit_contact_id').val();
    var _contact_name = $('#contact_name').val();
    var _contact_email = $('#contact_email').val();
    var _contact_tel = $('#contact_tel').val();
    var _contact_position = $('#contact_position').val();
    var _idx = $('#table_body input').length + 1;
    var html_new_line = "<input type='hidden' id='contact_name_contact_"+_edit_contact_id+"' name='contact_name' value='"+_contact_name+"'><input type='hidden' id='contact_email_contact_"+_edit_contact_id+"' name='contact_email' value='"+_contact_email+"'><input type='hidden' id='contact_tel_contact_"+_edit_contact_id+"' name='contact_tel' value='"+_contact_tel+"'><input type='hidden' id='contact_position_contact_"+_edit_contact_id+"' name='contact_position' value='"+_contact_position+"'><td style=\"width:70px;\"><button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:RemoveContact('"+_edit_contact_id+"');\"><span class='glyphicon glyphicon-trash' aria-hidden='true'></span></button> <button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:EditContact('"+_edit_contact_id+"');\"><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></button></td><td>"+_contact_name+"</td><td>"+_contact_email+"</td><td>"+_contact_tel+"</td><td>"+_contact_position+"</td>";
    // save line
    var html_body = html_new_line;
    
    $('#' + _edit_contact_id).html(html_body);
    $('#dialogModal').modal('hide');
  }
});

function AddContact() {
  var modal = $('#dialogModal')
  modal.find('.modal-title').text('Adicionar Contato');
  // Initialize contact name
  $('#contact_name').val('');
  // Initialize contact email
  $('#contact_email').val('');
  // Initialize contact tel
  $('#contact_tel').val('');
  // Initialize contact position
  $('#contact_position').val('');
  // Empty reference ID
  $('#edit_contact_id').val('');
  $('#btn_save').hide();
  $('#btn_add').show();
  // show modal
  modal.modal('show');
}

function RemoveContact(obj) {
  $('#' + obj).remove();
  if($('#table_body input').length == 0) {
    var _html_empty_line = "<tr> <td colspan=\"5\">Nenhum item adicionado</td></tr>";
    $('#table_body').html(_html_empty_line);
  }
}

function EditContact(obj) {
  $('#contact_name').val($('#' + obj + ' [name=contact_name]').val());
  $('#contact_email').val($('#' + obj + ' [name=contact_email]').val());
  $('#contact_tel').val($('#' + obj + ' [name=contact_tel]').val());
  $('#contact_position').val($('#' + obj + ' [name=contact_position]').val());

  var modal = $('#dialogModal')
  modal.find('.modal-title').text('Editar Contato')
  // Set reference ID
  $('#edit_contact_id').val(obj);
  $('#btn_save').show();
  $('#btn_add').hide();
  modal.modal('show');
}

function validate_form() {
  clear_validate_form();
  var _contact_name = $('#contact_name').val();
  var _return = true;
  if(_contact_name == "") {
    $('#contact_name').parent('.form-group').attr('class', 'form-group has-error');
    _return = false;
  }
  return _return;
}

function clear_validate_form() {
  $('#dialogModal .form-group').attr('class', 'form-group');
}

$('#dialogModal').on('shown.bs.modal', function () {
  clear_validate_form();
})
