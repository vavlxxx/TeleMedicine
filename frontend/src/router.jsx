/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from 'react'

const RouterContext = createContext(null)

function getCurrentLocation() {
  return {
    pathname: window.location.pathname.replace(/\/+$/, '') || '/',
    search: window.location.search || '',
    hash: window.location.hash || '',
  }
}

export function RouterProvider({ children }) {
  const [location, setLocation] = useState(getCurrentLocation)

  useEffect(() => {
    const handlePopState = () => {
      setLocation(getCurrentLocation())
    }

    window.addEventListener('popstate', handlePopState)

    return () => {
      window.removeEventListener('popstate', handlePopState)
    }
  }, [])

  const navigate = (to, options = {}) => {
    const nextUrl = typeof to === 'string' ? to : '/'
    const method = options.replace ? 'replaceState' : 'pushState'
    const resolvedUrl = new URL(nextUrl, window.location.origin)
    const nextLocation = `${resolvedUrl.pathname}${resolvedUrl.search}${resolvedUrl.hash}`

    window.history[method](null, '', nextLocation)
    setLocation(getCurrentLocation())

    if (resolvedUrl.hash) {
      window.requestAnimationFrame(() => {
        const targetId = decodeURIComponent(resolvedUrl.hash.slice(1))
        const targetElement = document.getElementById(targetId)

        if (targetElement) {
          targetElement.scrollIntoView({ block: 'start', behavior: 'auto' })
          return
        }

        window.scrollTo({ top: 0, behavior: 'auto' })
      })
      return
    }

    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  return <RouterContext.Provider value={{ location, navigate }}>{children}</RouterContext.Provider>
}

export function useRouter() {
  const context = useContext(RouterContext)

  if (!context) {
    throw new Error('useRouter must be used inside RouterProvider')
  }

  return context
}

export function AppLink({ href, className, children, ...props }) {
  const { navigate } = useRouter()
  const isExternalLink =
    typeof href === 'string' &&
    (href.startsWith('http://') ||
      href.startsWith('https://') ||
      href.startsWith('mailto:') ||
      href.startsWith('tel:'))

  const handleClick = (event) => {
    if (isExternalLink) {
      return
    }

    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return
    }

    event.preventDefault()
    navigate(href)
  }

  return (
    <a href={href} className={className} onClick={handleClick} {...props}>
      {children}
    </a>
  )
}
