import { useState } from 'react';
import Layout from 'components/Layout';
import { Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { register } from 'features/user';

const RegisterPage = () => {
	const dispatch = useDispatch();
	const { registered, loading } = useSelector(state => state.user);

	const [formData, setFormData] = useState({
		first_name: '',
		last_name: '',
		nickname: '',
		email: '',
		password: '',
	});

	const { first_name, last_name, email, nickname, password } = formData;

	const onChange = e => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

	const onSubmit = e => {
		e.preventDefault();

		dispatch(register({ first_name, last_name, nickname, email, password }));
	};

	if (registered) return <Navigate to='/login' />;

	return (
		<Layout title='Geo Duels | Register' content='Register page'>
			<h1 className='text-4xl font-bold text-white text-center m-5'>Register for an Account</h1>
			<form onSubmit={onSubmit}>
				<div className='mb-6'>
					<label className='block mb-2 text-sm font-medium text-white dark:text-gray-300' htmlFor='first_name'>
						First Name
					</label>
					<input
						className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
						type='text'
						name='first_name'
						onChange={onChange}
						value={first_name}
						required
					/>
				</div>
				<div className='mb-6'>
					<label className='block mb-2 text-sm font-medium text-white dark:text-gray-300' htmlFor='last_name'>
						Last Name
					</label>
					<input
						className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
						type='text'
						name='last_name'
						onChange={onChange}
						value={last_name}
						required
					/>
				</div>
				<div className='mb-6'>
					<label className='block mb-2 text-sm font-medium text-white dark:text-gray-300' htmlFor='nickname'>
						Nickname
					</label>
					<input
						className='bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
						type='text'
						name='nickname'
						onChange={onChange}
						value={nickname}
						required
					/>
				</div>
				<div className='mb-6mb-6'>
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
					<button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'>Register</button>
				)}
			</form>
		</Layout>
	);
};

export default RegisterPage;
