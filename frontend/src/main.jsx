import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import DoctorDirectoryWithFiltersPage from './DoctorDirectoryWithFiltersPage.jsx'
import DoctorPublicProfilePage from './DoctorPublicProfilePage.jsx'
import PublicQuestionsFeedPage from './PublicQuestionsFeedPage.jsx'
import LoginDesktopPage from './LoginDesktopPage.jsx'
import RegistrationDesktopPage from './RegistrationDesktopPage.jsx'

const pathname = window.location.pathname.replace(/\/+$/, '') || '/'
const pageByPath = {
  '/doctor-directory-with-filters-ru': DoctorDirectoryWithFiltersPage,
  '/doctor-public-profile-ru': DoctorPublicProfilePage,
  '/public-questions-feed-ru': PublicQuestionsFeedPage,
  '/login-desktop-ru': LoginDesktopPage,
  '/registration-desktop-ru': RegistrationDesktopPage,
}
const RootComponent = pageByPath[pathname] || App

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RootComponent />
  </StrictMode>,
)
