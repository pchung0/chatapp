$(document).ready(function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var current_room_id = -1;

    socket.on('connect', function () {
        console.log('connected:')
        socket.emit('my event', {
            data: 'User Connected'
        })
    })

    $('form#1').on('submit', function (e) {
        console.log('message sent!!')
        e.preventDefault()
        // let user_name = $('input.username').val()
        let user_input = $('input.message').val()
        socket.emit('send', {
            user_name: '{{ current_user.username }}',
            user_id: '{{ current_user.id }}',
            room_id: '{{ room_id }}',
            message: user_input
        })
        $('input.message').val('').focus()
    })

    $('#join').click(function () {
        let room = $('#room').val()
        socket.emit('join', room)
        $('h2#roomname').text(room)
        $('#room').val('')
    })

    $('#create').click(function () {
        let room = $('#room').val()
        socket.emit('create', room)
        // $('h2#roomname').text(room)
        $('#room').val('')
    })

    $("#leave").click(function () {
        socket.emit('leave')
        // $('h2#roomname').text('')
    })

    $(".room").click(function () {
        current_room_id = $(this).text()
        $('h2#roomname').text(current_room_id)
    })

    socket.on('room info', function (rooms) {
        // $('div.message_holder').append('<div><b style="color: #000">' + msg + '</b></div>')
        console.log(rooms)
    })

    socket.on('message', function (data) {
        console.log("{{ url_for('home') }}" + '/room')
        console.log('{{ room_id }}', data.room_id)
        if ('{{ room_id }}' == data.room_id)
            $('div.message_holder').append('<div><b style="color: #000">' + data.message + '</b></div>')
    })

    socket.on('my response', function (msg) {
        if (typeof msg.user_name !== 'undefined') {
            $('div.message_holder').append('<div><b style="color: #000">' + msg.user_name + '</b></div>')
        }
    })

    $('a.room').click(function () {
        $(this).addClass('active')
    })

})