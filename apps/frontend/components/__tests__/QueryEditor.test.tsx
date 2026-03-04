import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { QueryEditor } from '../QueryEditor'

describe('QueryEditor', () => {
  it('renders without crashing', () => {
    render(<QueryEditor />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('displays the initial value', () => {
    render(<QueryEditor value="SELECT * FROM users" />)
    expect(screen.getByRole('textbox')).toHaveValue('SELECT * FROM users')
  })

  it('calls onChange when text is entered', () => {
    const handleChange = jest.fn()
    render(<QueryEditor onChange={handleChange} />)

    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'SELECT 1' } })

    expect(handleChange).toHaveBeenCalledWith('SELECT 1')
  })

  it('calls onExecute when Execute button is clicked', async () => {
    const handleExecute = jest.fn()
    render(<QueryEditor value="SELECT 1" onExecute={handleExecute} />)

    const button = screen.getByText('Execute Query')
    fireEvent.click(button)

    await waitFor(() => {
      expect(handleExecute).toHaveBeenCalledWith('SELECT 1')
    })
  })

  it('disables Execute button when query is empty', () => {
    render(<QueryEditor value="" onExecute={jest.fn()} />)

    const button = screen.getByText('Execute Query')
    expect(button).toBeDisabled()
  })

  it('shows executing state while processing', async () => {
    const handleExecute = jest.fn(() => new Promise(resolve => setTimeout(resolve, 100)))
    render(<QueryEditor value="SELECT 1" onExecute={handleExecute} />)

    const button = screen.getByText('Execute Query')
    fireEvent.click(button)

    expect(screen.getByText('Executing...')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.queryByText('Executing...')).not.toBeInTheDocument()
    })
  })

  it('executes on Cmd/Ctrl + Enter', async () => {
    const handleExecute = jest.fn()
    render(<QueryEditor value="SELECT 1" onExecute={handleExecute} />)

    const textarea = screen.getByRole('textbox')
    fireEvent.keyDown(textarea, { key: 'Enter', metaKey: true })

    await waitFor(() => {
      expect(handleExecute).toHaveBeenCalledWith('SELECT 1')
    })
  })

  it('does not execute on Enter without modifier key', async () => {
    const handleExecute = jest.fn()
    render(<QueryEditor value="SELECT 1" onExecute={handleExecute} />)

    const textarea = screen.getByRole('textbox')
    fireEvent.keyDown(textarea, { key: 'Enter' })

    await waitFor(() => {
      expect(handleExecute).not.toHaveBeenCalled()
    })
  })

  it('is read-only when readOnly prop is true', () => {
    render(<QueryEditor readOnly />)

    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('readOnly')
  })

  it('shows Execute button by default', () => {
    render(<QueryEditor value="SELECT 1" />)

    expect(screen.getByText('Execute Query')).toBeInTheDocument()
  })

  it('hides Execute button when readOnly', () => {
    render(<QueryEditor value="SELECT 1" readOnly />)

    expect(screen.queryByText('Execute Query')).not.toBeInTheDocument()
  })
})
