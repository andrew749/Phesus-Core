let _ = require('lodash');

function goTo(path, params, method) {
    method = method || 'post';
    var form = document.createElement('form');
    form.setAttribute('method', method);
    form.setAttribute('action', path);
    _.chain(params)
      .map((v, k) => {
        var field = document.createElement('input');
        field.setAttribute('type', 'hidden');
        field.setAttribute('name', k);
        field.setAttribute('value', v);
        return field;
      }).each((field) => form.appendChild(field));

    document.body.appendChild(form);
    form.submit();
}

function onSignIn(googleUser) {
  let token = googleUser.getAuthResponse().id_token;
  goTo('signin', { token });
}
