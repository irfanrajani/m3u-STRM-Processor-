# Modern Frontend Redesign Plan
## Transform into a Sleek, Sexy, Modern IPTV Manager

**Vision**: Netflix-quality UI meets enterprise functionality
**Timeline**: 3-4 weeks
**Tech Stack**: React 18 + TailwindCSS + Framer Motion + Headless UI

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Modern Component Library](#2-modern-component-library)
3. [Sleek Dashboard Redesign](#3-sleek-dashboard-redesign)
4. [Channel Browser UX](#4-channel-browser-ux)
5. [VOD Library (Netflix-Style)](#5-vod-library-netflix-style)
6. [Provider Management UI](#6-provider-management-ui)
7. [Animations & Micro-interactions](#7-animations--micro-interactions)
8. [Dark Theme Perfection](#8-dark-theme-perfection)
9. [Performance Optimization](#9-performance-optimization)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Design Philosophy

### Core Principles

**1. Content First**
- Remove clutter, focus on content
- Large imagery (channel logos, posters)
- Generous whitespace
- Clear visual hierarchy

**2. Fluid & Responsive**
- Smooth animations (60fps)
- Responsive design (mobile → 4K)
- Touch-friendly interactions
- Keyboard navigation

**3. Dark-First Design**
- OLED-friendly pure black
- High contrast for readability
- Accent colors pop
- Optional light mode

**4. Premium Feel**
- Glassmorphism effects
- Subtle gradients
- Shadow depth
- Smooth transitions

### Color Palette

```javascript
// Modern dark theme
const colors = {
  // Backgrounds (layered depth)
  bg: {
    primary: '#0a0a0a',      // Pure black (OLED)
    secondary: '#141414',    // Card backgrounds
    tertiary: '#1e1e1e',     // Hover states
    elevated: '#2a2a2a'      // Modals/dropdowns
  },

  // Brand colors (vibrant, modern)
  brand: {
    primary: '#00d9ff',      // Cyan (electric)
    secondary: '#7c3aed',    // Purple (premium)
    gradient: 'linear-gradient(135deg, #00d9ff 0%, #7c3aed 100%)'
  },

  // Semantic colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',

  // Text (high contrast)
  text: {
    primary: '#ffffff',
    secondary: '#a1a1aa',
    tertiary: '#52525b',
    disabled: '#3f3f46'
  },

  // Borders & dividers
  border: '#27272a'
}
```

### Typography

```javascript
// Font stack
const typography = {
  sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', monospace",

  // Scale (fluid sizing)
  sizes: {
    xs: 'clamp(0.75rem, 0.7vw, 0.875rem)',
    sm: 'clamp(0.875rem, 0.85vw, 1rem)',
    base: 'clamp(1rem, 1vw, 1.125rem)',
    lg: 'clamp(1.125rem, 1.2vw, 1.25rem)',
    xl: 'clamp(1.25rem, 1.5vw, 1.5rem)',
    '2xl': 'clamp(1.5rem, 2vw, 1.875rem)',
    '3xl': 'clamp(1.875rem, 2.5vw, 2.25rem)',
    '4xl': 'clamp(2.25rem, 3vw, 3rem)'
  }
}
```

---

## 2. Modern Component Library

### Install Dependencies

```bash
cd frontend

# Core UI libraries
npm install @headlessui/react @heroicons/react
npm install framer-motion
npm install react-hot-toast

# Utilities
npm install clsx tailwind-merge
npm install react-intersection-observer
npm install @tanstack/react-virtual
```

### 2.1 Button Component (Sleek & Modern)

```typescript
// /frontend/src/components/ui/Button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'gradient'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      loading,
      disabled,
      icon,
      iconPosition = 'left',
      className,
      ...props
    },
    ref
  ) => {
    const baseClasses = `
      relative inline-flex items-center justify-center
      font-medium rounded-xl
      transition-all duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-bg-primary
      disabled:opacity-50 disabled:cursor-not-allowed
      overflow-hidden
    `

    const variants = {
      primary: `
        bg-brand-primary text-bg-primary
        hover:bg-brand-primary/90
        focus:ring-brand-primary/50
        shadow-lg shadow-brand-primary/20
        hover:shadow-xl hover:shadow-brand-primary/30
      `,
      secondary: `
        bg-bg-secondary text-text-primary
        hover:bg-bg-tertiary
        focus:ring-brand-primary/50
        border border-border
      `,
      ghost: `
        bg-transparent text-text-secondary
        hover:bg-bg-secondary hover:text-text-primary
        focus:ring-brand-primary/50
      `,
      danger: `
        bg-error text-white
        hover:bg-error/90
        focus:ring-error/50
        shadow-lg shadow-error/20
      `,
      gradient: `
        bg-gradient-to-r from-brand-primary to-brand-secondary
        text-white
        hover:shadow-xl hover:shadow-brand-primary/30
        focus:ring-brand-primary/50
      `
    }

    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2.5 text-base gap-2',
      lg: 'px-6 py-3.5 text-lg gap-2.5'
    }

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
        whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
        className={clsx(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {/* Shimmer effect on hover */}
        <span className="absolute inset-0 overflow-hidden rounded-xl">
          <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
        </span>

        {/* Content */}
        <span className="relative flex items-center gap-inherit">
          {loading ? (
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          ) : (
            <>
              {icon && iconPosition === 'left' && icon}
              {children}
              {icon && iconPosition === 'right' && icon}
            </>
          )}
        </span>
      </motion.button>
    )
  }
)
```

### 2.2 Glass Card Component

```typescript
// /frontend/src/components/ui/GlassCard.tsx
import { motion, HTMLMotionProps } from 'framer-motion'
import { clsx } from 'clsx'

interface GlassCardProps extends HTMLMotionProps<'div'> {
  blur?: 'sm' | 'md' | 'lg'
  border?: boolean
  glow?: boolean
}

export const GlassCard = ({
  children,
  blur = 'md',
  border = true,
  glow = false,
  className,
  ...props
}: GlassCardProps) => {
  const blurAmount = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        // Glass effect
        'bg-bg-secondary/50',
        blurAmount[blur],

        // Border
        border && 'border border-border',

        // Rounded corners
        'rounded-2xl',

        // Padding
        'p-6',

        // Glow effect
        glow && 'shadow-2xl shadow-brand-primary/10',

        // Hover effect
        'hover:bg-bg-secondary/60 transition-all duration-300',

        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
}
```

### 2.3 Modal Component (Sleek Overlay)

```typescript
// /frontend/src/components/ui/Modal.tsx
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
}

export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true
}: ModalProps) => {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl',
    full: 'max-w-full mx-4'
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" />
        </Transition.Child>

        {/* Modal container */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel
                as={motion.div}
                className={clsx(
                  'w-full',
                  sizes[size],
                  'transform overflow-hidden rounded-2xl',
                  'bg-bg-secondary border border-border',
                  'shadow-2xl',
                  'transition-all'
                )}
              >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-border">
                  <Dialog.Title className="text-xl font-semibold text-text-primary">
                    {title}
                  </Dialog.Title>

                  {showCloseButton && (
                    <button
                      onClick={onClose}
                      className="text-text-secondary hover:text-text-primary transition-colors p-1 rounded-lg hover:bg-bg-tertiary"
                    >
                      <XMarkIcon className="w-6 h-6" />
                    </button>
                  )}
                </div>

                {/* Content */}
                <div className="px-6 py-6">
                  {children}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
```

### 2.4 Input Component (Modern Form Fields)

```typescript
// /frontend/src/components/ui/Input.tsx
import { forwardRef, InputHTMLAttributes } from 'react'
import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  icon?: React.ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, icon, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              {icon}
            </div>
          )}

          <input
            ref={ref}
            className={clsx(
              // Base
              'w-full px-4 py-3 rounded-xl',
              'bg-bg-tertiary border border-border',
              'text-text-primary placeholder:text-text-tertiary',

              // Icon padding
              icon && 'pl-10',

              // Focus
              'focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary',

              // Transitions
              'transition-all duration-200',

              // Error state
              error && 'border-error focus:ring-error/50 focus:border-error',

              // Disabled
              'disabled:opacity-50 disabled:cursor-not-allowed',

              className
            )}
            {...props}
          />
        </div>

        {hint && !error && (
          <p className="mt-1.5 text-xs text-text-tertiary">{hint}</p>
        )}

        {error && (
          <p className="mt-1.5 text-xs text-error">{error}</p>
        )}
      </div>
    )
  }
)
```

---

## 3. Sleek Dashboard Redesign

### Modern Dashboard Layout

```typescript
// /frontend/src/pages/DashboardPage.tsx
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { GlassCard } from '@/components/ui/GlassCard'
import {
  ServerIcon,
  TvIcon,
  FilmIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

export const DashboardPage = () => {
  const { data: stats } = useQuery(['system-stats'], fetchSystemStats)

  const statCards = [
    {
      title: 'Providers',
      value: stats?.providers || 0,
      icon: ServerIcon,
      gradient: 'from-blue-500 to-cyan-500',
      change: '+2 this week'
    },
    {
      title: 'Channels',
      value: stats?.channels || 0,
      icon: TvIcon,
      gradient: 'from-purple-500 to-pink-500',
      change: '+150 today'
    },
    {
      title: 'VOD Content',
      value: stats?.vod || 0,
      icon: FilmIcon,
      gradient: 'from-orange-500 to-red-500',
      change: '+25 movies'
    },
    {
      title: 'Uptime',
      value: '99.8%',
      icon: CheckCircleIcon,
      gradient: 'from-green-500 to-emerald-500',
      change: 'Last 30 days'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold text-text-primary mb-2">
            Welcome back! 👋
          </h1>
          <p className="text-text-secondary text-lg">
            Here's what's happening with your IPTV streams today.
          </p>
        </div>

        <Button variant="gradient" size="lg">
          Add Provider
        </Button>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard
              className="group cursor-pointer hover:scale-105 transition-transform"
              glow
            >
              {/* Icon with gradient background */}
              <div className={`
                inline-flex p-3 rounded-xl mb-4
                bg-gradient-to-br ${card.gradient}
              `}>
                <card.icon className="w-6 h-6 text-white" />
              </div>

              {/* Value */}
              <div className="text-3xl font-bold text-text-primary mb-1">
                {card.value.toLocaleString()}
              </div>

              {/* Title */}
              <div className="text-sm text-text-secondary mb-2">
                {card.title}
              </div>

              {/* Change indicator */}
              <div className="text-xs text-brand-primary font-medium">
                {card.change}
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Activity Feed & Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <GlassCard>
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              Recent Activity
            </h2>
            <ActivityTimeline />
          </GlassCard>
        </div>

        {/* Quick Stats */}
        <div>
          <GlassCard>
            <h2 className="text-xl font-semibold text-text-primary mb-6">
              System Health
            </h2>
            <SystemHealthChart />
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
```

---

## 4. Channel Browser UX

### Netflix-Style Grid with Hover Effects

```typescript
// /frontend/src/pages/Channels.tsx
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

export const ChannelCard = ({ channel }) => {
  const [isHovered, setIsHovered] = useState(false)
  const { ref, inView } = useInView({ triggerOnce: true })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={inView ? { opacity: 1, scale: 1 } : {}}
      whileHover={{ scale: 1.05 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="relative group cursor-pointer"
    >
      {/* Card Container */}
      <div className="relative rounded-xl overflow-hidden bg-bg-secondary border border-border">
        {/* Logo */}
        <div className="aspect-video relative bg-bg-tertiary">
          <img
            src={channel.logo_url}
            alt={channel.name}
            className="w-full h-full object-contain p-4"
            loading="lazy"
          />

          {/* Quality Badge */}
          <div className="absolute top-3 right-3">
            <span className={`
              px-2 py-1 rounded-lg text-xs font-bold
              ${channel.quality === '4K' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                channel.quality === '1080p' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' :
                'bg-bg-elevated'}
              text-white shadow-lg
            `}>
              {channel.quality}
            </span>
          </div>

          {/* Stream Count Badge */}
          {channel.stream_count > 1 && (
            <div className="absolute bottom-3 left-3">
              <span className="px-2 py-1 rounded-lg text-xs font-medium bg-bg-elevated/80 backdrop-blur-sm text-text-secondary">
                {channel.stream_count} streams
              </span>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="p-4">
          <h3 className="font-semibold text-text-primary truncate mb-1">
            {channel.name}
          </h3>
          <p className="text-sm text-text-secondary truncate">
            {channel.category}
          </p>

          {/* EPG Indicator */}
          {channel.has_epg && (
            <div className="flex items-center gap-1 mt-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-xs text-text-tertiary">EPG Available</span>
            </div>
          )}
        </div>

        {/* Hover Overlay */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-end justify-center p-6"
            >
              <div className="space-y-3 w-full">
                <Button variant="gradient" className="w-full" size="sm">
                  Watch Now
                </Button>
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" className="flex-1">
                    Info
                  </Button>
                  <Button variant="ghost" size="sm" className="flex-1">
                    Favorite
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
```

---

## 5. VOD Library (Netflix-Style)

### Horizontal Scrolling Rows

```typescript
// /frontend/src/components/VOD/MovieRow.tsx
import { useRef } from 'react'
import { motion } from 'framer-motion'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline'

export const MovieRow = ({ title, movies }) => {
  const scrollRef = useRef<HTMLDivElement>(null)

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = scrollRef.current.clientWidth * 0.8
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      })
    }
  }

  return (
    <div className="space-y-4 group">
      {/* Row Title */}
      <h2 className="text-2xl font-bold text-text-primary px-8">
        {title}
      </h2>

      {/* Scrollable Row */}
      <div className="relative">
        {/* Left Arrow */}
        <button
          onClick={() => scroll('left')}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-12 h-full bg-gradient-to-r from-bg-primary to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-start pl-2"
        >
          <div className="p-2 bg-bg-elevated/80 backdrop-blur-sm rounded-full hover:bg-bg-elevated transition-colors">
            <ChevronLeftIcon className="w-6 h-6 text-text-primary" />
          </div>
        </button>

        {/* Movies Container */}
        <div
          ref={scrollRef}
          className="flex gap-4 overflow-x-auto scrollbar-hide px-8 pb-4"
        >
          {movies.map((movie, index) => (
            <motion.div
              key={movie.id}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex-none w-48 group/card"
            >
              {/* Movie Poster */}
              <div className="relative rounded-lg overflow-hidden mb-3">
                <img
                  src={movie.cover_url}
                  alt={movie.title}
                  className="w-full aspect-[2/3] object-cover group-hover/card:scale-110 transition-transform duration-300"
                />

                {/* Rating Badge */}
                <div className="absolute top-2 right-2">
                  <span className="px-2 py-1 rounded-md text-xs font-bold bg-yellow-500 text-black">
                    ⭐ {movie.rating}
                  </span>
                </div>

                {/* Gradient Overlay on Hover */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover/card:opacity-100 transition-opacity flex items-end p-4">
                  <Button size="sm" variant="gradient" className="w-full">
                    Play
                  </Button>
                </div>
              </div>

              {/* Movie Info */}
              <h3 className="font-medium text-text-primary truncate">
                {movie.title}
              </h3>
              <p className="text-sm text-text-secondary">
                {movie.year} · {movie.duration}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Right Arrow */}
        <button
          onClick={() => scroll('right')}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-12 h-full bg-gradient-to-l from-bg-primary to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-end pr-2"
        >
          <div className="p-2 bg-bg-elevated/80 backdrop-blur-sm rounded-full hover:bg-bg-elevated transition-colors">
            <ChevronRightIcon className="w-6 h-6 text-text-primary" />
          </div>
        </button>
      </div>
    </div>
  )
}
```

---

## 6. Provider Management UI

### Modern Provider Cards

```typescript
// /frontend/src/pages/Providers.tsx
export const ProviderCard = ({ provider }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <GlassCard className="group">
      <div className="flex items-start justify-between">
        {/* Left: Provider Info */}
        <div className="flex items-start gap-4">
          {/* Provider Icon */}
          <div className={`
            w-12 h-12 rounded-xl flex items-center justify-center
            ${provider.enabled ? 'bg-gradient-to-br from-green-500 to-emerald-500' :
              'bg-bg-tertiary'}
          `}>
            <ServerIcon className="w-6 h-6 text-white" />
          </div>

          {/* Info */}
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-text-primary">
                {provider.name}
              </h3>
              <span className={`
                px-2 py-0.5 rounded-md text-xs font-medium
                ${provider.type === 'xstream' ? 'bg-blue-500/20 text-blue-400' :
                  'bg-purple-500/20 text-purple-400'}
              `}>
                {provider.type.toUpperCase()}
              </span>
            </div>

            <p className="text-sm text-text-secondary mb-3">
              {provider.total_channels} channels · Priority {provider.priority}
            </p>

            {/* Stats Row */}
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-text-tertiary">
                  {provider.active_channels} active
                </span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <span className="text-text-tertiary">
                  {provider.total_channels - provider.active_channels} failed
                </span>
              </div>
              <span className="text-text-tertiary">
                Last sync: {formatRelativeTime(provider.last_sync)}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => syncProvider(provider.id)}
          >
            Sync
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Less' : 'More'}
          </Button>
        </div>
      </div>

      {/* Expanded Section */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mt-6 pt-6 border-t border-border"
          >
            <ProviderDetails provider={provider} />
          </motion.div>
        )}
      </AnimatePresence>
    </GlassCard>
  )
}
```

---

## 7. Animations & Micro-interactions

### Page Transitions

```typescript
// /frontend/src/components/PageTransition.tsx
import { motion } from 'framer-motion'

export const PageTransition = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.3, ease: 'easeInOut' }}
  >
    {children}
  </motion.div>
)

// Use in routes:
<Route path="/dashboard" element={
  <PageTransition>
    <DashboardPage />
  </PageTransition>
} />
```

### Loading Skeletons

```typescript
// /frontend/src/components/ui/Skeleton.tsx
export const Skeleton = ({ className }) => (
  <div className={clsx(
    'animate-pulse bg-bg-tertiary rounded-lg',
    className
  )} />
)

// Channel Card Skeleton
export const ChannelCardSkeleton = () => (
  <div className="rounded-xl bg-bg-secondary border border-border p-4">
    <Skeleton className="w-full aspect-video mb-4" />
    <Skeleton className="h-5 w-3/4 mb-2" />
    <Skeleton className="h-4 w-1/2" />
  </div>
)
```

### Toast Notifications (Sleek)

```typescript
// /frontend/src/lib/toast.ts
import toast from 'react-hot-toast'

export const showToast = {
  success: (message: string) => toast.success(message, {
    style: {
      background: '#141414',
      color: '#fff',
      border: '1px solid #27272a',
      borderRadius: '12px',
      padding: '16px'
    },
    iconTheme: {
      primary: '#10b981',
      secondary: '#141414'
    }
  }),

  error: (message: string) => toast.error(message, {
    style: {
      background: '#141414',
      color: '#fff',
      border: '1px solid #27272a',
      borderRadius: '12px',
      padding: '16px'
    },
    iconTheme: {
      primary: '#ef4444',
      secondary: '#141414'
    }
  })
}
```

---

## 8. Dark Theme Perfection

### TailwindCSS Configuration

```javascript
// /frontend/tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0a0a0a',
          secondary: '#141414',
          tertiary: '#1e1e1e',
          elevated: '#2a2a2a'
        },
        brand: {
          primary: '#00d9ff',
          secondary: '#7c3aed'
        },
        text: {
          primary: '#ffffff',
          secondary: '#a1a1aa',
          tertiary: '#52525b',
          disabled: '#3f3f46'
        },
        border: '#27272a',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        'glow': '0 0 20px rgba(0, 217, 255, 0.3)',
        'glow-lg': '0 0 40px rgba(0, 217, 255, 0.4)'
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-brand': 'linear-gradient(135deg, #00d9ff 0%, #7c3aed 100%)'
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('tailwind-scrollbar-hide')
  ]
}
```

---

## 9. Performance Optimization

### Virtual Scrolling for Large Lists

```typescript
// /frontend/src/pages/Channels.tsx
import { useVirtualizer } from '@tanstack/react-virtual'

export const VirtualChannelList = ({ channels }) => {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: channels.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 250,
    overscan: 5
  })

  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative'
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          >
            <ChannelCard channel={channels[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## 10. Implementation Roadmap

### Week 1: Foundation
- [ ] Install dependencies (Headless UI, Framer Motion)
- [ ] Set up TailwindCSS dark theme
- [ ] Create base component library (Button, Input, Card, Modal)
- [ ] Update global styles and typography

### Week 2: Dashboard & Layout
- [ ] Redesign Dashboard with glass cards
- [ ] Create modern navigation/sidebar
- [ ] Add page transitions
- [ ] Implement loading skeletons

### Week 3: Content Pages
- [ ] Redesign Channel browser with hover effects
- [ ] Build Netflix-style VOD library
- [ ] Update Provider management UI
- [ ] Add animations and micro-interactions

### Week 4: Polish & Optimization
- [ ] Virtual scrolling for large lists
- [ ] Image lazy loading
- [ ] Performance audit
- [ ] Accessibility improvements
- [ ] Final testing

**Total: 3-4 weeks for complete UI overhaul**

---

**Result**: A modern, sleek, sexy IPTV manager that looks and feels like a premium Netflix-quality application! 🚀
