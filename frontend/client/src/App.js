import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { checkAuth } from 'features/user';

import HomePage from 'containers/HomePage';
import LoginPage from 'containers/LoginPage';
import RegisterPage from 'containers/RegisterPage';
import FriendsPage from 'containers/FriendsPage';
import UsersPage from 'containers/UsersPage';
import CreateRoomPage from 'containers/CreateRoomPage';
import InviteFriendsPage from 'containers/InviteFriendsPage';
import InvitesPage from 'containers/InvitesPage';
import PlayRoomPage from 'containers/PlayRoomPage';
import MatchRoomPage from 'containers/MatchRoomPage';
import SinglePlayerMatchPage from 'containers/SinglePlayerMatchPage';
import ProxyHomePage from 'containers/ProxyHomePage';
import ProxySinglePlayerMatchPage from 'containers/ProxySinglePlayerMatchPage';

const App = () => {
	const dispatch = useDispatch();

	useEffect(() => {
		dispatch(checkAuth());
	}, []);

	return (
		<Router>
			<Routes>
				<Route path='/' element={<HomePage />} />
				<Route path='/home' element={<HomePage />} />
				<Route path='/proxy-home' element={<ProxyHomePage />} />
				<Route path='/login' element={<LoginPage />} />
				<Route path='/register' element={<RegisterPage />} />
				<Route path='/friends' element={<FriendsPage />} />
				<Route path='/users' element={<UsersPage />} />
				<Route path='/create-room' element={<CreateRoomPage />} />
				<Route path='/invite-friends' element={<InviteFriendsPage />} />
				<Route path='/invites' element={<InvitesPage />} />
				<Route path='/play' element={<PlayRoomPage />} />
				<Route path='/match' element={<MatchRoomPage />} />
				<Route path='/single-player-match' element={<SinglePlayerMatchPage />} />
				<Route path='/proxy-single-player-match' element={<ProxySinglePlayerMatchPage />} />
			</Routes>
		</Router>
	);
};

export default App;
