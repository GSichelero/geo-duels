import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { joinRoom } from 'features/user';
import Layout from 'components/Layout';

const PlayRoomPage = () => {
	const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, createdRoom, friends, users, friendRequestsReceived, friendRequestsSent, joinedRoom } = useSelector(
		state => state.user
	);

	const [formData, setFormData] = useState({
		room_name: '',
		room_password: '',
	});

	const { room_name, room_password } = formData;

	const onChange = e => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

	const onSubmit = e => {
		e.preventDefault();

		dispatch(joinRoom({ room_name, room_password }));
	};

	if (registered) return <Navigate to='/login' />;

	if (!isAuthenticated && !loading && user === null)
		return <Navigate to='/login' />;

	if (isAuthenticated && joinedRoom) return <Navigate to='/match' />;
	
	return (
		<Layout title='Geo Duels | Login' content='Login page'>
			<h1 className='text-4xl font-bold text-white text-center m-5'>Enter a Match</h1>
			<form onSubmit={onSubmit}>
			<div className='mb-3 mt-5'>
                                <label htmlFor='room_name' className='block mb-2 text-sm font-medium text-white dark:text-gray-300'>
                                    Room Name
                                </label>
                                <input
                                    type='text'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
                                    id='room_name'
                                    name='room_name'
                                    value={room_name}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='room_password' className='block mb-2 text-sm font-medium text-white dark:text-gray-300'>
                                    Room Password
                                </label>
                                <input
                                    type='text'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
                                    id='room_password'
                                    name='room_password'
                                    value={room_password}
                                    onChange={onChange}
                                    required
                                />
                            </div>
				{loading ? (
					<div className='spinner-border text-primary' role='status'>
						<span className='visually-hidden text-white'>Loading...</span>
					</div>
				) : (
					<button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'>Join Room</button>
				)}
			</form>
		</Layout>
	);
};

export default PlayRoomPage;
