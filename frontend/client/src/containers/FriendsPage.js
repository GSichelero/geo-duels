import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import ClosingAlert from 'components/Alert';
import { getFriends, sendFriendRequest, getAllUsers, getFriendRequestsReceived, getFriendRequestsSent, cancelFriendRequest, rejectFriendRequest, acceptFriendRequest, removeFriend } from 'features/user';

const UsersPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, friends, users, friendRequestsReceived, friendRequestsSent } = useSelector(state => state.user);

    useEffect(() => {
        dispatch(getFriendRequestsReceived());
        dispatch(getFriends());
    }, []);

	if (!isAuthenticated && !loading && user === null)
		return <Navigate to='/login' />;

    return (
        <Layout title='Geo Duels | All users' content='All users page'>
            {loading || user === null ? (
                <div className='spinner-border text-primary' role='status'>
                    <span className='visually-hidden'>Loading...</span>
                </div>
            ) : (
                <>
                <ClosingAlert text={'Here you can see all your friends and the friend requests you have received!'} color={'yellow'} />
                <div className='grid grid-cols-2 justify-center'>
                    <div className='justify-center'>
                        <h1 className='mb-5 text-white text-3xl font-bold'>Your Friends</h1>
                        <ul>
                        <table>
                            {friends.map((friend) => (
                                <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center'>
                                    <td className='text-white font-bold text-bold text-center'>{friend.nickname}</td>
                                    <td>
                                        <button className='text-white text-bold bg-red-600 hover:bg-red-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                                        onClick={() => dispatch(removeFriend(friend.id))}>
                                            Remove friend
                                        </button>
                                    </td>
                                </tr>
                            ))}
                                </table>
                        </ul>
                    </div>
                    <div>
                        <h1 className='mb-5 text-white text-3xl font-bold'>Friend Requests Received</h1>
                        <ul>
                        <table>
                            {friendRequestsReceived.map((friend) => (
                                <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center justify-center'>
                                    <td className='text-white font-bold text-bold text-center'>{friend.from_user.nickname}</td>
                                    <td>
                                        <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                                        onClick={() => dispatch(acceptFriendRequest(friend.id))}>
                                            Accept
                                        </button>
                                    </td>
                                    <td>
                                        <button className='text-white text-bold bg-red-600 hover:bg-red-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                                        onClick={() => dispatch(rejectFriendRequest(friend.id))}>
                                            Reject
                                        </button>
                                    </td>
                                </tr>
                            ))}
                                </table>
                        </ul>
                    </div>
                </div>
                </>
            )}
        </Layout>
    );
};

export default UsersPage;