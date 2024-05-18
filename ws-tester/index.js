import { io } from 'socket.io-client'

const socket = io('http://localhost:8888')

socket.on('connect', _ => {
    console.log('connected')
})
