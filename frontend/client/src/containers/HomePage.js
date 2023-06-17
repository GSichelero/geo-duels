import Layout from 'components/Layout';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { getFriends, createSinglePlayerRoom, joinSinglePlayerRoom } from 'features/user';


let room_name = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
let room_password = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
let max_members = 2;
let number_of_rounds = 5;
let time_per_pick = 30;
let time_per_guess = 300;
let moving_allowed = false;

const HomePage = () => {
	const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, createdRoom, friends, users, friendRequestsReceived, friendRequestsSent, joinedRoom } = useSelector(state => state.user);

	if (createdRoom && !joinedRoom) {
		dispatch(joinSinglePlayerRoom({ room_name, room_password }));
	}

	if (joinedRoom) return <Navigate to='/single-player-match' />;


	return (
		<Layout title='Geo Duels | Home' content='Home page'>
			<h1 className="text-7xl font-bold text-white text-center m-12">Geo Duels</h1>
			<button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full py-3 px-4 mt-1 mb-4'
			onClick = {() => dispatch(createSinglePlayerRoom({ room_name, room_password, max_members, number_of_rounds, time_per_pick, time_per_guess, moving_allowed }))}>
				Play Single Player Match
			</button>
			<button className='text-white font-medium bg-green-500 hover:bg-green-600 focus:ring-4 focus:outline-none focus:ring-green-300 rounded-lg text-sm w-full py-1 px-4 mt-1 mb-4'
			onClick={() => window.open('https://forms.gle/q3veh4SMVVEAxkQ89', '_blank')}>
				Answer a quick survey about your experience with the website! Your feedback is very valuable
			</button>
			<img className="w-2/5 mx-auto filter-white" src="globe-icon.svg" alt="Geo Duels Logo" />
		</Layout>
	);
};

export default HomePage;
