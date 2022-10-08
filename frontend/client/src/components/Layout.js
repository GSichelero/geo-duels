import { Helmet } from 'react-helmet';
import Navbar from 'components/Navbar';

const Layout = ({ title, content, children }) => (
	<>
		<Helmet>
			<title>{title}</title>
			<meta name='description' content={content} />
		</Helmet>
		<Navbar />
		<div className='md:container md:mx-auto'>{children}</div>
	</>
);

export default Layout;
