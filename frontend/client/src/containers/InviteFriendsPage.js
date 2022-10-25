import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import { getFriends, inviteFriend } from 'features/user';

const InviteFriendsPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, friends, users, friendRequestsReceived, friendRequestsSent, createdRoom } = useSelector(state => state.user);

    useEffect(() => {
        dispatch(getFriends());
    }, []);

	if (!isAuthenticated && !loading && user === null)
		return <Navigate to='/login' />;

    console.log(createdRoom.roomId);

    return (
        <Layout title='Geo Duels | All users' content='All users page'>
            {loading || user === null ? (
                <div className='spinner-border text-primary' role='status'>
                    <span className='visually-hidden'>Loading...</span>
                </div>
            ) : (
                <>
                <div className='grid grid-cols-2 justify-center'>
                    <div className='justify-center'>
                        <h1 className='mb-5 text-white text-3xl font-bold'>Your Friends</h1>
                        <ul>
                        <table>
                            {friends.map((friend) => (
                                <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center'>
                                    <td className='text-white font-bold text-bold text-center'>{friend.nickname}</td>
                                    <td>
                                        <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
                                        onClick={() => dispatch(inviteFriend({'friend_username':friend.nickname, 'room_id':createdRoom.roomId}))}>
                                            Invite Friend
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

export default InviteFriendsPage;