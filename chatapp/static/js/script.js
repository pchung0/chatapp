$(document).ready(() => {
  const socket = io.connect(`http://${document.domain}:${location.port}`);
  let current_room_id;
  let current_room_name;
  let current_room_owner;
  const current_user_id = $('#username').attr('data-user-id');
  const current_username = $('#username').text();

  socket.on('connect', () => {
    socket.emit('my event', {
      data: 'User Connected',
    });
  });

  socket.on('message', (msg) => {
    if (current_room_id === msg.room_id) {
      if (current_username === msg.username) {
        append_receiver_chat_box(msg.message, msg.datetime);
      } else {
        append_sender_chat_box(msg.message, msg.datetime, msg.username);
      }
      scroll_bottom('chat-box');
    } else {
      $(`#room-list .room[data-room-id=${msg.room_id}] i`).removeClass('d-none');
    }
  });

  $('#invite-input').on('keyup', (e) => {
    const value = $(e.currentTarget).val().toLowerCase();

    $('.dropdown-menu a').filter(
      (_, node) => $(node).toggle($(node).text().toLowerCase().indexOf(value) > -1),
    );

    $('.input-holder span').each((_, element) => {
      const username = $(element).text();
      $(`.dropdown-menu a:contains('${username}')`).toggle(false);
    });
  });

  $('#invite-input').on('keydown', (e) => {
    if ($(e.currentTarget).val() === '' && e.which === 8) {
      $(e.currentTarget).prev().remove();
    }
  });

  $('#invite-input').focus(() => {
    $('.dropdown').dropdown('show');
  });

  $('.dropdown-menu').on('click', 'a', (e) => {
    e.preventDefault();
    const username = $(e.currentTarget).html();
    $(e.currentTarget).toggle(false);
    $('#invite-input').before(`<span class="badge badge-secondary align-self-center mr-1">${username}</span>`);
    $('#invite-input').val('').focus();
  });

  $('.modal').on('shown.bs.modal', (e) => {
    $(e.currentTarget).find('input').focus();
    if ($(e.currentTarget).attr('id') === 'invite-modal') {
      $('#username-dropdown').empty();
      get_not_in_room_users(current_room_id).then((users) => {
        users.forEach(
          (item) => $('#username-dropdown').append(`<a class="dropdown-item" href="#">${item}</a>`),
        );
      });
    }
  });

  $('.modal').on('hidden.bs.modal', (e) => {
    $('input').val('');
    if ($(e.currentTarget).attr('id') === 'invite-modal') {
      $('.dropdown').find('span').remove();
      $('.dropdown').dropdown('hide');
    }
  });

  $('div#room-list').on('click', 'a.room', (e) => {
    e.preventDefault();
    const room_id = parseInt($(e.currentTarget).attr('href'), 10);

    $('#room-list a.active').addClass('list-group-item-light').removeClass('active');
    $(e.currentTarget).addClass('active').removeClass('list-group-item-light');
    $('div.chat-box').empty();
    load_room(room_id);
    history.pushState('data to be passed', '', `/rooms/${room_id}`);
  });

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

  $('#invite-form').on('submit', (e) => {
    e.preventDefault();
    const users = [];
    $('.input-holder span').each((_, element) => { users.push($(element).text()); });
    $('#invite-modal').modal('hide');
    invite_room(current_room_id, users).then(() => {
      update_member_list(current_room_id);
    });
  });

  $('#create-form').on('submit', (e) => {
    e.preventDefault();
    const room_name = $('#create-room-input').val();
    create_room(room_name).then((room) => {
      load_room_list(room.id);
      $('div.chat-box').empty();
      load_room(room.id);
      history.pushState('data to be passed', '', `/rooms/${room.id}`);
    });
    $('#create-modal').modal('hide');
  });

  $('#confirm-delete').find('.btn-ok').click(() => {
    $('#confirm-delete').modal('hide');
    $('#chatroom-title').text('');
    $('.room-modal').addClass('d-none');
    $('#room-list a.active').remove();
    $('div.chat-box').empty();
    delete_room(current_room_id);
    history.pushState('data to be passed', '', '');
  });

  $('#join').click(() => {
    const room = $('#room').val();
    socket.emit('join', room);
    $('h2#roomname').text(room);
    $('#room').val('');
  });

  $('#leave').click(() => {
    socket.emit('leave');
  });

  function init() {
    let room_id = -1;
    if (window.location.pathname.match(/^\/rooms\/[0-9]+$/g)) {
      room_id = window.location.pathname.split('/').slice(-1)[0];
      load_room(room_id);
    }
    load_room_list(room_id);
  }

  function load_room(room_id) {
    $('.room-modal').removeClass('d-none');
    $(`#room-list .room[data-room-id= ${room_id}] i`).addClass('d-none'); // remove notification dot

    get_room(room_id).then((room) => {
      current_room_id = room.id;
      current_room_name = room.name;
      current_room_owner = room.owner;

      room.users[0] = `${room.users[0]} (owner)`;
      $('#chatroom-title').attr('title', `Members:\n${room.users.join('\n')}`);
      $('#chatroom-title').text(current_room_name);
      $('.current-room').text(current_room_name);
      update_delete_leave_button(current_username === current_room_owner);
      render_messages(room.messages);
      scroll_bottom('chat-box');
    });
  }

  function update_delete_leave_button(bool) {
    if (bool) {
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
    get_room_members(room_id).then((usernames) => {
      const users = usernames;
      users[0] = `${users[0]} (owner)`;
      $('#chatroom-title').attr('title', `Members:\n${users.join('\n')}`);
    });
  }

  function scroll_bottom(id) {
    const chat_box = document.getElementById(id);
    chat_box.scrollTop = chat_box.scrollHeight;
  }

  function render_messages(messages) {
    messages.forEach((msg) => {
      if (msg.username === current_username) {
        append_receiver_chat_box(msg.message, msg.datetime);
      } else {
        append_sender_chat_box(msg.message, msg.datetime, msg.username);
      }
    });
  }

  function append_sender_chat_box(message, datetime, username) {
    $('div.chat-box').append(
      `
            <div class="media w-50 mb-3"><img
                    src="https://res.cloudinary.com/mhmd/image/upload/v1564960395/avatar_usae7z.svg" alt="user"
                    width="50" class="rounded-circle">
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

  function append_receiver_chat_box(message, datetime) {
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

  function load_room_list(activate_room_id) {
    $('div#room-list').empty();
    get_room_list().then((rooms) => {
      rooms.forEach((room) => {
        append_room_list(room.id, room.name, room.owner_id, activate_room_id === room.id);
      });
    });
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

  const get_room_list = async () => {
    const response = await fetch('/api/rooms');
    const room_list = await response.json();
    return room_list;
  };

  const get_room = async (room_id) => {
    const response = await fetch(`/api/rooms/${room_id}`);
    const messages = await response.json();
    return messages;
  };

  const get_not_in_room_users = async (room_id) => {
    const response = await fetch(`/api/users?room=${room_id}&nonmembers=1`);
    const users = await response.json();
    return users;
  };

  const get_room_members = async (room_id) => {
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

  const invite_room = async (room_id, usernames) => {
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
