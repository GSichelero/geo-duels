import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Layout from 'components/Layout';
import { getAllUsers } from 'features/user';

const FriendsPage = () => {
    const dispatch = useDispatch();
	const { isAuthenticated, user, loading, users } = useSelector(state => state.user);

    useEffect(() => {
        dispatch(getAllUsers());
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
                    <h1 className='mb-5'>All Users</h1>
                    <p>User Details</p>
                    <ul>
                        {users.map((user) => (
                            <li>
                                <p>{user.first_name}</p>
                                <p>{user.last_name}</p>
                                <p>{user.email}</p>
                                <button>Add as friend</button>
                            </li>
                        ))}
                    </ul>
                </>
            )}
        </Layout>
    );
};

export default FriendsPage;