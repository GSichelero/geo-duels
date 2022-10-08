import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { resetRegistered, login } from 'features/user';
import Layout from 'components/Layout';

const LoginPage = () => {
	const dispatch = useDispatch();
	const { loading, isAuthenticated, registered, previousPath } = useSelector(
		state => state.user
	);

	const [formData, setFormData] = useState({
		email: '',
		password: '',
	});

	useEffect(() => {
		if (registered) dispatch(resetRegistered());
	}, [registered]);

	const { email, password } = formData;

	const onChange = e => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

	const onSubmit = e => {
		e.preventDefault();

		dispatch(login({ email, password }));
	};

	if (isAuthenticated) return <Navigate to={`${previousPath}`} />;

	return (
		<Layout title='Geo Duels | Login' content='Login page'>
			<h1 className='text-4xl font-bold text-white text-center m-5'>Log into your Account</h1>
			<form onSubmit={onSubmit}>
				<div className='mb-6'>
					<label className='block mb-2 text-sm font-medium text-white dark:text-gray-300' htmlFor='email'>
						Email
					</label>
					<input
						className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
						type='email'
						name='email'
						onChange={onChange}
						value={email}
						required
					/>
				</div>
				<div className='mb-6'>
					<label className='block mb-2 text-sm font-medium text-white dark:text-gray-300' htmlFor='password'>
						Password
					</label>
					<input
						className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
						type='password'
						name='password'
						onChange={onChange}
						value={password}
						required
					/>
				</div>
				{loading ? (
					<div className='spinner-border text-primary' role='status'>
						<span className='visually-hidden text-white'>Loading...</span>
					</div>
				) : (
					<button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'>Login</button>
				)}
			</form>
		</Layout>
	);
};

export default LoginPage;
