/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './apps/**/*.{ts,tsx}',
    './packages/**/*.{ts,tsx}',
    './docs/**/*.{md}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary brand colors
        brand: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6', // Electric Blue (Accent)
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E3A8A', // Brand Blue (Primary)
          900: '#1E3A8A',
          950: '#172554',
        },

        // Accent colors
        accent: {
          blue: '#3B82F6',
          purple: '#8B5CF6',
        },

        // Neutral colors
        neutral: {
          50: '#F9FAFB',
          100: '#F3F4F6', // Light Gray (Surface)
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280', // Gray (Text)
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937', // Dark Gray (Heading)
          900: '#111827',
          950: '#030712',
        },

        // Dark mode colors
        slate: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B', // Dark Mode Surface
          900: '#0F172A', // Dark Mode Background
          950: '#020617',
        },

        // Semantic colors
        success: {
          50: '#D1FAE5',
          100: '#A7F3D0',
          200: '#6EE7B7',
          300: '#34D399',
          400: '#10B981',
          500: '#059669',
          600: '#047857',
          700: '#065F46',
          800: '#064E3B',
          900: '#064E3B',
        },

        warning: {
          50: '#FEF3C7',
          100: '#FDE68A',
          200: '#FCD34D',
          300: '#FBBF24',
          400: '#F59E0B',
          500: '#D97706',
          600: '#B45309',
          700: '#92400E',
          800: '#78350F',
          900: '#713F12',
        },

        error: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },

        info: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
      },

      fontFamily: {
        sans: [
          'Inter',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Consolas',
          'Monaco',
          'monospace',
        ],
      },

      fontSize: {
        // Display scale
        'display-xl': ['48px', { lineHeight: '56px', fontWeight: '700' }],
        'display-lg': ['36px', { lineHeight: '44px', fontWeight: '600' }],
        'display-md': ['30px', { lineHeight: '40px', fontWeight: '600' }],

        // Body scale
        'body-lg': ['18px', { lineHeight: '28px', fontWeight: '400' }],
        'body-base': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'body-sm': ['14px', { lineHeight: '20px', fontWeight: '400' }],

        // Caption
        'caption': ['12px', { lineHeight: '16px', fontWeight: '500' }],
      },

      spacing: {
        // Base unit: 4px
        'xs': '4px',
        'sm': '8px',
        'md': '16px', // Base spacing
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },

      borderRadius: {
        'xs': '4px',  // Buttons, inputs
        'sm': '4px',  // Buttons, inputs
        'md': '8px',  // Cards, containers
        'lg': '12px', // Modals, panels
        'xl': '16px', // Hero sections
      },

      boxShadow: {
        // Elevation scale
        'xs': '0 1px 2px rgba(0,0,0,0.05)',
        'sm': '0 1px 3px rgba(0,0,0,0.1)',
        'md': '0 4px 6px rgba(0,0,0,0.1)',
        'lg': '0 10px 15px rgba(0,0,0,0.1)',
        'xl': '0 20px 25px rgba(0,0,0,0.15)',
      },

      animation: {
        'fade-in': 'fadeIn 0.2s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
