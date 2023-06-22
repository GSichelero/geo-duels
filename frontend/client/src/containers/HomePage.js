import Layout from 'components/Layout';

const HomePage = () => {

	const handleClick = () => {
		window.location.href = '/proxy-single-player-match';
	  };

	return (
		<Layout title='Geo Duels | Home' content='Home page'>
			<h1 className="text-7xl font-bold text-white text-center m-12">Geo Duels</h1>
			<button className='text-blue-700 text-bold bg-white hover:bg-blue-100 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full py-3 px-4 mt-1 mb-4'
			onClick={handleClick}>
				Play Single Player Match
			</button>
			<button className='text-white font-medium bg-green-500 hover:bg-green-600 focus:ring-4 focus:outline-none focus:ring-green-300 rounded-lg text-sm w-full py-1 px-4 mt-1 mb-4'
			onClick={() => window.open('https://forms.gle/q3veh4SMVVEAxkQ89', '_blank')}>
				Answer a quick survey about your experience with the website! Your feedback is very valuable
			</button>
			<img className="w-2/5 mx-auto filter-white" src="globe-icon.svg" alt="Geo Duels Logo" />
		</Layout>
	);
};

export default HomePage;
