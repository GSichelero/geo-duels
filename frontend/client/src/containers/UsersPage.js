import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import ClosingAlert from 'components/Alert';
import { getFriends, sendFriendRequest, getAllUsers, getFriendRequestsReceived, getFriendRequestsSent, cancelFriendRequest } from 'features/user';

const UsersPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, friends, users, friendRequestsReceived, friendRequestsSent } = useSelector(state => state.user);

    useEffect(() => {
        dispatch(getFriendRequestsSent());
        dispatch(getFriendRequestsReceived());
        dispatch(getFriends());
        dispatch(getAllUsers());
    }, []);

	if (!isAuthenticated && !loading && user === null)
		return <Navigate to='/login' />;

    let filteredUsers = users;
    if (user) {
        filteredUsers = users.filter((outer_user) => outer_user.id !== user.id);

        filteredUsers = filteredUsers.filter((outer_user) => {
            let isFriend = false;
            friends.forEach((friend) => {
                if (friend.id === outer_user.id) {
                    isFriend = true;
                }
            });
            return !isFriend;
        });

        filteredUsers = filteredUsers.filter((outer_user) => {
            let isFriendRequestSent = false;
            friendRequestsSent.forEach((friend) => {
                if (friend.to_user.id === outer_user.id) {
                    isFriendRequestSent = true;
                }
            });
            return !isFriendRequestSent;
        });

        filteredUsers = filteredUsers.filter((outer_user) => {
            let isFriendRequestReceived = false;
            friendRequestsReceived.forEach((friend) => {
                if (friend.from_user.id === outer_user.id) {
                    isFriendRequestReceived = true;
                }
            });
            return !isFriendRequestReceived;
        });
    }

    return (
        <Layout title='Geo Duels | All users' content='All users page'>
            {loading || user === null ? (
                <div className='spinner-border text-primary' role='status'>
                    <span className='visually-hidden'>Loading...</span>
                </div>
            ) : (
                <>
                <ClosingAlert text={'Here you can see all users that you may want to add as your friends and the yet unanswered friend requests you have already sent!'} color={'yellow'} />
                <div className='grid grid-cols-2 justify-center'>
                    <div className='justify-center'>
                        <h1 className='mb-5 text-white text-3xl font-bold'>All Users</h1>
                        <ul>
                        <table>
                            {filteredUsers.map((friend) => (
                                <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center'>
                                    <td className='text-white font-bold text-bold text-center'>{friend.nickname}</td>
                                    <td>
                                        <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
                                        onClick={() => dispatch(sendFriendRequest(friend.id))}>
                                            Add as friend
                                        </button>
                                    </td>
                                </tr>
                            ))}
                                </table>
                        </ul>
                    </div>
                    <div>
                        <h1 className='mb-5 text-white text-3xl font-bold'>Friend Requests Sent</h1>
                        <ul>
                        <table>
                            {friendRequestsSent.map((friend) => (
                                <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center justify-center'>
                                    <td className='text-white font-bold text-bold text-center'>{friend.to_user.nickname}</td>
                                    <td>
                                        <button className='text-white text-bold bg-red-600 hover:bg-red-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
                                        onClick={() => dispatch(cancelFriendRequest(friend.id))}>
                                            Cancel
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