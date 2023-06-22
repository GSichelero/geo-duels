import Layout from 'components/Layout';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { getFriends, createRoom, joinRoom, resetRooms } from 'features/user';


const ProxySinglePlayerMatchPage = () => {
	const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, createdRoom, friends, users, friendRequestsReceived, friendRequestsSent, joinedRoom } = useSelector(state => state.user);

	if (createdRoom || joinedRoom) {
		dispatch(resetRooms());
	}
    else {
        window.location.reload();
        return <Navigate to="/single-player-match"/>;
    }


	return (
		<Layout title='Geo Duels | Home' content='Home page'>
			<h1 className="text-7xl font-bold text-white text-center m-12">Geo Duels</h1>
			<img className="w-2/5 mx-auto filter-white" src="globe-icon.svg" alt="Geo Duels Logo" />
		</Layout>
	);
};

export default ProxySinglePlayerMatchPage;