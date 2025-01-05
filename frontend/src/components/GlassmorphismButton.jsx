import React from 'react';

const GlassmorphismButton = ({
    children,
    className,
    ...props
}) => {
    const baseClasses = [
        'px-6 py-3 rounded-lg',
        'bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg',
        'border border-white border-opacity-20',
        'text-white font-semibold',
        'shadow-lg',
        'transition-all duration-300 ease-in-out',
        'hover:bg-opacity-20 hover:shadow-xl',
        'focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50',
        'active:bg-opacity-30 active:scale-95',
        'glow-effect'
    ].join(' ');

    return (
        <button
            className={`${baseClasses} ${className || ''}`}
            {...props}
        >
            {children}
        </button>
    );
};

export default GlassmorphismButton;
