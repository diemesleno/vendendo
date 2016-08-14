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
    var _service_id = $('#sel_services option:selected').val();
    var _service_name = $('#sel_services option:selected').text();
    var _description = $('#description_text').val();
    var _expected_amount = $('#expected_amount').val();
    var _expected_value = $('#expected_value').val();
    var html_body = $('#table_body').html();
    var _idx = get_new_idx();
    var html_new_line = "<tr id=\"item_"+_idx+"\"><input type='hidden' id='product_item_"+_idx+"' name='product' value='"+_service_id+"'><input type='hidden' id='description_item_"+_idx+"' name='description' value='"+_description+"'><input type='hidden' id='expected_amount_item_"+_idx+"' name='expected_amount' value='"+_expected_amount+"'><input type='hidden' id='expected_value_item_"+_idx+"' name='expected_value_item' value='"+_expected_value+"'><td style=\"width:70px;\"><button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:RemoveService('item_"+_idx+"');\"><span class='glyphicon glyphicon-trash' aria-hidden='true'></span></button> <button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:EditService('item_"+_idx+"');\"><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></button></td><td>"+_service_name+"</td><td>"+_description+"</td><td>"+_expected_amount+"</td><td>"+_expected_value+"</td></tr>";
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
    var _edit_service_id = $('#edit_service_id').val();
    var _service_id = $('#sel_services option:selected').val();
    var _service_name = $('#sel_services option:selected').text();
    var _description = $('#description_text').val();
    var _expected_amount = $('#expected_amount').val();
    var _expected_value = $('#expected_value').val();
    var _idx = $('#table_body input').length + 1;
    var html_new_line = "<input type='hidden' id='product_"+_edit_service_id+"' name='product' value='"+_service_id+"'><input type='hidden' id='description_"+_edit_service_id+"' name='description' value='"+_description+"'><input type='hidden' id='expected_amount_"+_edit_service_id+"' name='expected_amount' value='"+_expected_amount+"'><input type='hidden' id='expected_value_"+_edit_service_id+"' name='expected_value_item' value='"+_expected_value+"'><td style=\"width:70px;\"><button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:RemoveService('"+_edit_service_id+"');\"><span class='glyphicon glyphicon-trash' aria-hidden='true'></span></button> <button type=\"button\" class=\"btn btn-default btn-xs\" onclick=\"javascript:EditService('"+_edit_service_id+"');\"><span class='glyphicon glyphicon-pencil' aria-hidden='true'></span></button></td><td>"+_service_name+"</td><td>"+_description+"</td><td>"+_expected_amount+"</td><td>"+_expected_value+"</td>";
    // save line
    var html_body = html_new_line;
    
    $('#' + _edit_service_id).html(html_body);
    $('#dialogModal').modal('hide');
  }
});

function AddService() {
  var modal = $('#dialogModal')
  modal.find('.modal-title').text('Adicionar Produto/Serviço');
  // Set first option
  $('#sel_services option')[0].selected = true
  // Initialize description text
  $('#description_text').val('');
  // Initialize expected amount
  $('#expected_amount').val('1');
  // Initialize expected value
  $('#expected_value').val('0.00');
  // Empty reference ID
  $('#edit_service_id').val('');
  $('#btn_save').hide();
  $('#btn_add').show();
  // show modal
  modal.modal('show');
}

function RemoveService(obj) {
  $('#' + obj).remove();
  if($('#table_body input').length == 0) {
    var _html_empty_line = "<tr> <td colspan=\"5\">Nenhum item adicionado</td></tr>";
    $('#table_body').html(_html_empty_line);
  }
}

function EditService(obj) {
  $('#sel_services').val($('#' + obj + ' [name=product]').val());
  $('#description_text').val($('#' + obj + ' [name=description]').val());
  $('#expected_amount').val($('#' + obj + ' [name=expected_amount]').val());
  $('#expected_value').val($('#' + obj + ' [name=expected_value_item]').val());

  var modal = $('#dialogModal')
  modal.find('.modal-title').text('Editar Produto/Serviço')
  // Set reference ID
  $('#edit_service_id').val(obj);
  $('#btn_save').show();
  $('#btn_add').hide();
  modal.modal('show');
}

function validate_form() {
  clear_validate_form();
  var _service_id = $('#sel_services option:selected').val();
  var _expected_amount = $('#expected_amount').val();
  var _expected_value = $('#expected_value').val();
  var _return = true;
  if(parseInt(_service_id) <= 0) {
    $('#sel_services').parent('.form-group').attr('class', 'form-group has-error');
    _return = false;
  }
  if(parseInt(_expected_amount) < 1 || !_expected_amount) {
    $('#expected_amount').parent('.form-group').attr('class', 'form-group has-error');
    _return = false;
  } 
  if(parseInt(_expected_value) < 0 || !_expected_value) {
    $('#expected_value').parent('.form-group').attr('class', 'form-group has-error');
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
