import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import { getFriends, createRoom } from 'features/user';
import useWebSocket from 'react-use-websocket';

const MatchRoomPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, joinedRoom } = useSelector(state => state.user);
    let room_name = 'socketserver';
    const url = `ws://127.0.0.1:8000/ws/room/${room_name}/`;

    const { lastJsonMessage, sendMessage } = useWebSocket(url, {
    onOpen: () => console.log(`Connected to App WS`),
    onMessage: () => {
        if (lastJsonMessage) {
        console.log(lastJsonMessage);
        // setNumero(lastJsonMessage.n);
        }
    },
    // queryParams: { 'token': '123456' },
    onError: (event) => { console.error(event); },
    shouldReconnect: (closeEvent) => true,
    reconnectInterval: 3000
    });

	return (
		<Layout title='Geo Duels | Home' content='Home page'>
			<h1 className="text-7xl font-bold text-white text-center m-12">Geo Duels</h1>
		</Layout>
	);
};

export default MatchRoomPage;