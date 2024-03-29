import { Link, NavLink } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from 'features/user';

const Navbar = () => {
	const dispatch = useDispatch();
	const { isAuthenticated } = useSelector(state => state.user);

	const authLinks = (
		<>
			<li className='block py-2 pr-4 pl-3 text-gray-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0'>
				<NavLink className='block py-2 pr-4 pl-3 text-pink-500 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-yellow-500 md:p-0' to='/play'>
					Play
				</NavLink>
			</li>
			<li className='block py-2 pr-4 pl-3 text-gray-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0'>
				<NavLink className='block py-2 pr-4 pl-3 text-purple-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-red-700 md:p-0' to='/create-room'>
					Create Room
				</NavLink>
			</li>
			<li className='block py-2 pr-4 pl-3 text-gray-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0'>
				<NavLink className='block py-2 pr-4 pl-3 text-purple-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-red-700 md:p-0' to='/invites'>
					Invites
				</NavLink>
			</li>
			<li className='block py-2 pr-4 pl-3 text-gray-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0'>
				<NavLink className='block py-2 pr-4 pl-3 text-yellow-500 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-pink-500 md:p-0' to='/friends'>
					Friends
				</NavLink>
			</li>
			<li className='block py-2 pr-4 pl-3 text-gray-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0'>
				<NavLink className='block py-2 pr-4 pl-3 text-yellow-500 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-pink-500 md:p-0' to='/users'>
					Add Friends
				</NavLink>
			</li>
			<li className='block py-2 pr-4 pl-3 text-gray-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0'>
				<a className='block py-2 pr-4 pl-3 text-red-700 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-purple-700 md:p-0' href='#!' onClick={() => dispatch(logout())}>
					Logout
				</a>
			</li>
		</>
	);

	const guestLinks = (
		<>
			<li>
				<NavLink className='block py-2 pr-4 pl-3 text-pink-500 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0' to='/login'>
					Login
				</NavLink>
			</li>
			<li>
				<NavLink className='block py-2 pr-4 pl-3 text-pink-500 rounded hover:bg-gray-100 md:hover:bg-transparent md:border-0 md:hover:text-blue-700 md:p-0' to='/register'>
					Register
				</NavLink>
			</li>
		</>
	);

	return (
		<nav className='bg-white border-gray-200 px-2 sm:px-4 py-1'>
			<div className='container flex flex-wrap justify-between items-center mx-auto'>
				<Link className='flex items-center' to='/proxy-home'>
				<span class="text-purple-700 md:hover:text-pink-500 self-center text-xl font-semibold whitespace-nowrap">Geo Duels</span>
				</Link>
				<button data-collapse-toggle="navbar-default" type="button" class="inline-flex items-center p-2 ml-3 text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200" aria-controls="navbar-default" aria-expanded="false">
					<span class="sr-only">Open main menu</span>
					
				</button>
				<div className='hidden w-full md:block md:w-auto' id='navbar-default'>
					<ul className='flex flex-col p-4 mt-4 bg-gray-50 rounded-lg border border-gray-100 md:flex-row md:space-x-8 md:mt-0 md:text-sm md:font-medium md:border-0 md:bg-white'>
						{isAuthenticated ? authLinks : guestLinks}
					</ul>
				</div>
			</div>
		</nav>
	);
};

export default Navbar;
