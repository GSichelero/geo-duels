import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import ClosingAlert from 'components/Alert';
import { getFriends, inviteFriend, getReceivedInvites, rejectInvite, joinRoom } from 'features/user';

const InvitesPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, friends, createdRoom, receivedInvites, joinedRoom } = useSelector(state => state.user);

    useEffect(() => {
        dispatch(getReceivedInvites());
    }, []);

	if (!isAuthenticated && !loading && user === null)
		return <Navigate to='/login' />;

    if (isAuthenticated && joinedRoom) return <Navigate to='/match' />;

    return (
        <Layout title='Geo Duels | All users' content='All users page'>
            {loading || user === null ? (
                <div className='spinner-border text-primary' role='status'>
                    <span className='visually-hidden'>Loading...</span>
                </div>
            ) : (
                <>
                <ClosingAlert text={'Here you can see the invites you have received to join matches created by other players!'} color={'pink'} />
                <div className='grid grid-cols-2 justify-center'>
                    <div className='justify-center'>
                        <h1 className='mb-5 text-white text-3xl font-bold'>Yours Match's Invites</h1>
                        <ul>
                        <table>
                            {receivedInvites.map((invite) => (
                                <tr className=' focus:outline-white rounded-lg w-full sm:w-auto px-5 py-2.5 text-center'>
                                    <td className='text-white font-bold text-bold text-center pr-6'>Room: {invite.roomName}</td>
                                    <td className='text-white font-bold text-bold text-center pr-5'>Host: {invite.roomOwner}</td>
                                    <td className='pr-3'>
                                        <button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                                        onClick={() => dispatch(joinRoom({'room_name':invite.roomName, 'room_password':invite.roomPassword}))}>
                                            Join Match
                                        </button>
                                    </td>
                                    <td>
                                        <button className='text-white text-bold bg-red-600 hover:bg-red-400 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center'
                                        onClick={() => dispatch(rejectInvite({'room_id':invite.roomId}))}>
                                            Reject Invite
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

export default InvitesPage;