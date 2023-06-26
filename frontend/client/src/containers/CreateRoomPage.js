import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import { getFriends, createRoom } from 'features/user';

const CreateRoomPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, registered, createdRoom, friends, users, friendRequestsReceived, friendRequestsSent } = useSelector(state => state.user);

    useEffect(() => {
        dispatch(getFriends());
    }, []);

    const [formData, setFormData] = useState({
		room_name: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15),
		room_password: '',
		max_members: 2,
		number_of_rounds: 1,
		time_per_pick: 60,
        time_per_guess: 60,
        moving_allowed: false,
	});

	const {  room_name, room_password, max_members, number_of_rounds, time_per_pick, time_per_guess, moving_allowed } = formData;

	const onChange = e => {
        if (e.target.name == 'max_members' || e.target.name == 'number_of_rounds' || e.target.name == 'time_per_pick' || e.target.name == 'time_per_guess') {
            if (e.target.value < 1 && e.target.name != 'max_members') {
                e.target.value = 1;
            }
            else if (e.target.value < 2 && e.target.name == 'max_members') {
                e.target.value = 2;
            }
            else if ((e.target.name == 'max_members' || e.target.name == 'number_of_rounds') && e.target.value > 10) {
                e.target.value = 10;
            }
        }
        setFormData({ ...formData, [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
    };

	const onSubmit = e => {
		e.preventDefault();

		dispatch(createRoom({ room_name, room_password, max_members, number_of_rounds, time_per_pick, time_per_guess, moving_allowed }));
	};

	if (registered) return <Navigate to='/login' />;

	if (!isAuthenticated && !loading && user === null)
		return <Navigate to='/login' />;
    
    if (createdRoom)
        return <Navigate to='/invite-friends' />;

    return (
        <Layout title='Geo Duels | Create Room' content='Create Room page'>
            {loading || user === null ? (
                <div className='spinner-border text-primary' role='status'>
                    <span className='visually-hidden'>Loading...</span>
                </div>
            ) : (
                <>
                <div className='grid grid-cols-10'>
                    <div className='col-span-4'>
                        <h1 className='text-4xl font-bold text-white text-center m-5'>Create Room</h1>
                    </div>
                <div className='col-span-6'>
                <form onSubmit={onSubmit}>
                            <div className='mb-3 mt-5'>
                                <label htmlFor='room_name' className='block mb-2 text-sm font-medium text-white'>
                                    Room Name
                                </label>
                                <input
                                    type='text'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                    id='room_name'
                                    name='room_name'
                                    value={room_name}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='room_password' className='block mb-2 text-sm font-medium text-white'>
                                    Room Password
                                </label>
                                <input
                                    type='text'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                    id='room_password'
                                    name='room_password'
                                    value={room_password}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='max_members' className='block mb-2 text-sm font-medium text-white'>
                                    Number of Players
                                </label>
                                <input
                                    type='number'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                    id='max_members'
                                    name='max_members'
                                    value={max_members}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='number_of_rounds' className='block mb-2 text-sm font-medium text-white'>
                                    Number of Rounds
                                </label>
                                <input
                                    type='number'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                    id='number_of_rounds'
                                    name='number_of_rounds'
                                    value={number_of_rounds}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='time_per_pick' className='block mb-2 text-sm font-medium text-white'>
                                    Time per Pick (seconds)
                                </label>
                                <input
                                    type='number'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                    id='time_per_pick'
                                    name='time_per_pick'
                                    value={time_per_pick}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='time_per_guess' className='block mb-2 text-sm font-medium text-white'>
                                    Time per Guess (seconds)
                                </label>
                                <input
                                    type='number'
                                    className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                    id='time_per_guess'
                                    name='time_per_guess'
                                    value={time_per_guess}
                                    onChange={onChange}
                                    required
                                />
                            </div>
                            <div className='mb-3'>
                                <label htmlFor='moving_allowed' className='inline-block text-sm font-medium text-white'>
                                    Moving Allowed
                                </label>
                                <input
                                    type='checkbox'
                                    className='h-4 w-4 border border-gray-300 rounded-sm bg-white checked:bg-blue-600 checked:border-blue-600 focus:outline-none transition duration-200 mt-1 align-top bg-no-repeat bg-center bg-contain float-left mr-2 cursor-pointer'
                                    id='moving_allowed'
                                    name='moving_allowed'
                                    value={moving_allowed}
                                    onChange={onChange}
                                />
                            </div>
                            {loading ? (
                                <div className='spinner-border text-primary' role='status'>
                                    <span className='visually-hidden text-white'>Loading...</span>
                                </div>
                            ) : (
                                <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'>Create Room</button>
                            )}
                        </form>
                        </div>
                </div>
                </>
            )}
        </Layout>
    );
};

export default CreateRoomPage;