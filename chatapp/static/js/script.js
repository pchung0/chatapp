$(document).ready(() => {
  const socket = io.connect(`http://${document.domain}:${window.location.port}`);
  let current_room_id;
  let current_room_name;
  let current_room_owner;
  const current_user_id = $('#username').attr('data-user-id');
  const current_username = $('#username').text();

  function init() {
    if (window.location.pathname.match(/^\/rooms\/[0-9]+$/g)) {
      const room_id = parseInt(window.location.pathname.split('/').slice(-1)[0], 10);
      load_room_list(room_id);
      load_room(room_id);
    } else {
      load_room_list();
    }

    register_socket_events();
    register_invite_input_dropdown_events();
    register_modal_confirm_button_events();
    register_toggle_modal_events();
    register_change_room_event();
    register_send_message_event();

    window.onpopstate = (event) => {
      if ('room_id' in event.state) {
        load_room(event.state.room_id);
      }
    };
  }

  function register_socket_events() {
    socket.on('connect', () => {
      socket.emit('my event', {
        data: 'User Connected',
      });
    });

    socket.on('message', (msg) => {
      if (current_room_id === msg.room_id) {
        append_messages([msg]);
        scroll_to_bottom('chat-box');
      } else {
        show_notification_dot(msg.room_id);
      }
    });
  }

  function register_change_room_event() {
    $('div#room-list').on('click', 'a.room', (e) => {
      e.preventDefault();
      const room_id = parseInt($(e.currentTarget).attr('href'), 10);
      load_room(room_id);
      window.history.pushState({ room_id }, '', `/rooms/${room_id}`);
    });
  }

  function register_send_message_event() {
    $('#message-form').on('submit', (e) => {
      e.preventDefault();
      if (current_room_id) {
        const user_input = $('#message-input-box').val();
        if (user_input) {
          socket.emit('send', {
            username: current_username,
            user_id: current_user_id,
            room_id: current_room_id,
            message: user_input,
          });
        }
      }
      $('#message-input-box').val('').focus();
    });
  }

  function register_toggle_modal_events() {
    $('.modal').on('shown.bs.modal', (e) => {
      if ($(e.currentTarget).attr('id') === 'invite-modal') {
        build_invite_dropdown();
      }
      $(e.currentTarget).find('input').focus();
    });

    $('.modal').on('hidden.bs.modal', (e) => {
      $('input').val('');
      if ($(e.currentTarget).attr('id') === 'invite-modal') {
        $('.dropdown').find('span').remove();
        $('.dropdown').dropdown('hide');
      }
    });
  }

  function register_modal_confirm_button_events() {
    $('#invite-form').on('submit', (e) => {
      e.preventDefault();
      const users = [];
      $('.input-holder span').each((_, element) => { users.push($(element).text()); });
      $('#invite-modal').modal('hide');
      invite_users(current_room_id, users).then(() => {
        update_member_list(current_room_id);
      });
    });

    $('#create-form').on('submit', (e) => {
      e.preventDefault();
      const room_name = $('#create-room-input').val();
      create_room(room_name).then((room) => {
        load_room_list(room.id);
        load_room(room.id);
        window.history.pushState({ room_id: room.id }, '', `/rooms/${room.id}`);
      });
      $('#create-modal').modal('hide');
    });

    $('#confirm-delete').find('.btn-ok').click(() => {
      $('#confirm-delete').modal('hide');
      clear_room();
      delete_room(current_room_id);
      window.history.pushState({}, '', '/');
    });
  }

  function register_invite_input_dropdown_events() {
    $('#invite-input').on('keyup', (e) => {
      const user_input = $(e.currentTarget).val().toLowerCase();

      // filter out usernames that do not partially match the user input
      $('.dropdown-menu a').filter(
        (_, item) => $(item).toggle($(item).text().toLowerCase().indexOf(user_input) > -1),
      );

      // filter out already selected usernames
      $('.input-holder span').each((_, username) => {
        $(`.dropdown-menu a:contains('${$(username).text()}')`).toggle(false);
      });
    });

    $('#invite-input').on('keydown', (e) => {
      const no_input_and_backspace_pressed = $(e.currentTarget).val() === '' && e.which === 8;
      if (no_input_and_backspace_pressed) {
        $(e.currentTarget).prev().remove();
      }
    });

    $('#invite-input').on('focus', () => {
      $('.dropdown').dropdown('show');
    });

    $('.dropdown-menu').on('click', 'a', (e) => {
      e.preventDefault();
      $(e.currentTarget).toggle(false);
      const username = $(e.currentTarget).html();
      $('#invite-input').before(`<span class="badge badge-secondary align-self-center mr-1">${username}</span>`);
      $('#invite-input').val('').focus();
    });
  }

  function show_notification_dot(room_id) {
    $(`.room[data-room-id=${room_id}] i`).removeClass('d-none');
  }

  function hide_notification_dot(room_id) {
    $(`.room[data-room-id=${room_id}] i`).addClass('d-none');
  }

  function build_invite_dropdown() {
    $('#username-dropdown').empty();
    fetch_room_nonmembers(current_room_id).then((users) => {
      users.forEach(
        (item) => $('#username-dropdown').append(`<a class="dropdown-item" href="#">${item}</a>`),
      );
    });
  }

  function load_room_list(activate_room_id = -1) {
    $('div#room-list').empty();
    fetch_room_list().then((rooms) => {
      rooms.forEach((room) => {
        append_room_list(room.id, room.name, room.owner_id, activate_room_id === room.id);
      });
    });
  }

  function clear_room() {
    $('#chatroom-title').text('');
    $('.room-modal').addClass('d-none');
    $('#room-list a.active').remove();
    $('div.chat-box').empty();
  }

  function load_room(room_id) {
    $('#room-list a.active').removeClass('active');
    $(`.room[data-room-id=${room_id}]`).addClass('active');
    $('div.chat-box').empty();
    $('.room-modal').removeClass('d-none');
    hide_notification_dot(room_id);

    fetch_room(room_id).then((room) => {
      current_room_id = room.id;
      current_room_name = room.name;
      current_room_owner = room.owner;
      const usernames = room.users;
      usernames[0] = `${usernames[0]} (owner)`;
      $('#chatroom-title').attr('title', `Members:\n${room.users.join('\n')}`);
      $('#chatroom-title').text(current_room_name);
      $('.current-room').text(current_room_name);
      update_delete_leave_button(current_username === current_room_owner);
      append_messages(room.messages);
      scroll_to_bottom('chat-box');
    });
  }

  function update_delete_leave_button(is_delete) {
    if (is_delete) {
      $('.delete-leave').text('Delete');
      $('i.fa-trash').removeClass('d-none');
      $('i.fa-sign-out').addClass('d-none');
    } else {
      $('.delete-leave').text('Leave');
      $('i.fa-trash').addClass('d-none');
      $('i.fa-sign-out').removeClass('d-none');
    }
  }

  function update_member_list(room_id) {
    fetch_room_members(room_id).then((usernames) => {
      const users = usernames;
      users[0] = `${users[0]} (owner)`;
      $('#chatroom-title').attr('title', `Members:\n${users.join('\n')}`);
    });
  }

  function scroll_to_bottom(id) {
    const chat_box = document.getElementById(id);
    chat_box.scrollTop = chat_box.scrollHeight;
  }

  function append_messages(messages) {
    messages.forEach((msg) => {
      if (msg.username === current_username) {
        append_receiver_message(msg.message, msg.datetime);
      } else {
        append_sender_message(msg.message, msg.datetime, msg.username);
      }
    });
  }

  function append_sender_message(message, datetime, username) {
    $('div.chat-box').append(
      `
      <div class="media w-50 mb-3">
        <div class="media-body ml-3">
          <div class="bg-light rounded py-2 px-3 mb-2">
            <p class="text-small font-weight-bold">${username}</p>
            <p class="text-small mb-0 text-muted">${message}</p>
          </div>
          <p class="small text-muted font-weight-light">${datetime}</p>
        </div>
      </div>
      `,
    );
  }

  function append_receiver_message(message, datetime) {
    $('div.chat-box').append(
      `
      <div class="media w-50 ml-auto mb-3">
        <div class="media-body">
          <div class="bg-primary rounded py-2 px-3 mb-2">
            <p class="text-small mb-0 text-white">${message}</p>
          </div>
          <p class="small text-muted">${datetime}</p>
        </div>
      </div>
      `,
    );
  }

  function append_room_list(id, name, owner_id, activate) {
    $('div#room-list').append(
      `
      <a href="${id}" class="${activate ? 'active ' : ''}room list-group-item list-group-item-action rounded-0"
      data-room-id="${id}" data-room-name="${name}" data-room-owner-id="${owner_id}">
        <div class="media">
          <div class="media-body ml-2">
            <div class="d-flex align-items-center justify-content-between mb-1">
              <h6 class="mb-0">${name}</h6>
              <i class="fa fa-circle text-primary d-none" style="font-size:10px;"></i>
            </div>
          </div>
        </div>
      </a>
      `,
    );
  }

  const fetch_room_list = async () => {
    const response = await fetch('/api/rooms');
    const room_list = await response.json();
    return room_list;
  };

  const fetch_room = async (room_id) => {
    const response = await fetch(`/api/rooms/${room_id}`);
    const messages = await response.json();
    return messages;
  };

  const fetch_room_nonmembers = async (room_id) => {
    const response = await fetch(`/api/users?room=${room_id}&nonmembers=1`);
    const users = await response.json();
    return users;
  };

  const fetch_room_members = async (room_id) => {
    const response = await fetch(`/api/rooms/${room_id}/users`);
    const users = await response.json();
    return users;
  };

  const create_room = async (new_room_name) => {
    const response = await fetch('/api/rooms', {
      method: 'POST',
      body: JSON.stringify({ room_name: new_room_name }),
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  };

  const invite_users = async (room_id, usernames) => {
    await fetch(`/api/rooms/${room_id}/users`, {
      method: 'POST',
      body: JSON.stringify({ room_id, users: usernames }),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  };

  const delete_room = async (room_id) => {
    await fetch(`/api/rooms/${room_id}`, {
      method: 'DELETE',
    });
  };

  init();
});
